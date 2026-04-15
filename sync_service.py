"""
Servicio de sincronizacion de reparaciones hacia API central externa.
"""

import logging
import os
import sqlite3
from datetime import datetime

import requests


logger = logging.getLogger("sync_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s sync_service: %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def _load_dotenv(dotenv_path=".env"):
    """Carga variables simples KEY=VALUE desde .env sin dependencias extra."""
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def _default_sqlite_path():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "database", "sistema_ventas.db")


def _load_config():
    _load_dotenv()
    return {
        "api_base": (os.environ.get("CENTRAL_API_BASE") or "").rstrip("/"),
        "api_key": os.environ.get("CENTRAL_API_KEY", ""),
        "sqlite_path": os.environ.get("SQLITE_PATH") or _default_sqlite_path(),
        "timeout": int(os.environ.get("CENTRAL_API_TIMEOUT", "12") or "12"),
    }


def get_sync_interval_seconds(default_value=300):
    """Intervalo de sync automático en segundos. 0 desactiva el scheduler."""
    _load_dotenv()
    raw = os.environ.get("CENTRAL_SYNC_INTERVAL_SECONDS", str(default_value))
    try:
        value = int(raw)
    except Exception:
        value = default_value

    return max(0, value)


def _connect(sqlite_path):
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


def _map_estado(estado_db):
    mapa = {
        "en_proceso": "en_proceso",
        "en_espera_retiro": "en_espera_retiro",
        "retirado": "retirado",
    }
    return mapa.get(estado_db, "en_proceso")


def _to_payload(row):
    actualizado_raw = row["fecha_entrega"] or row["fecha_creacion"] or datetime.now().strftime("%Y-%m-%d")
    actualizado = str(actualizado_raw)[:10]

    dispositivo = (row["dispositivo"] or "").strip()
    modelo = (row["modelo"] or "").strip()
    equipo = dispositivo if not modelo else f"{dispositivo} {modelo}"

    return {
        "external_id": row["external_id"] or row["numero_orden"],
        "dni": (row["cliente_dni"] or "").strip(),
        "equipo": equipo,
        "falla": (row["problema"] or "").strip(),
        "estado": _map_estado(row["estado"]),
        "actualizado": actualizado,
    }


def get_sync_status():
    config = _load_config()
    sqlite_path = config["sqlite_path"]

    conn = _connect(sqlite_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM reparaciones")
    total = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM reparaciones WHERE sync_pending = 1")
    pendientes = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM reparaciones WHERE synced_at IS NOT NULL")
    sincronizadas = cur.fetchone()["c"]

    cur.execute(
        """
        SELECT id, numero_orden, sync_attempts, last_sync_error
        FROM reparaciones
        WHERE sync_pending = 1
        ORDER BY sync_attempts DESC, id ASC
        LIMIT 10
        """
    )
    muestra = [dict(row) for row in cur.fetchall()]
    conn.close()

    return {
        "sqlite_path": sqlite_path,
        "total": total,
        "pendientes": pendientes,
        "sincronizadas": sincronizadas,
        "muestra_pendientes": muestra,
    }


def run_sync_once(limit=None):
    """Sincroniza reparaciones pendientes una sola pasada."""
    config = _load_config()

    if not config["api_base"] or not config["api_key"]:
        msg = "Faltan CENTRAL_API_BASE o CENTRAL_API_KEY en .env"
        logger.error(msg)
        return {
            "ok": False,
            "error": msg,
            "enviadas": 0,
            "fallidas": 0,
        }

    conn = _connect(config["sqlite_path"])
    cur = conn.cursor()

    query = """
        SELECT id, numero_orden, external_id, cliente_dni, dispositivo, modelo, problema, estado,
               fecha_creacion, fecha_entrega, sync_attempts
        FROM reparaciones
        WHERE sync_pending = 1
        ORDER BY id ASC
    """
    if limit:
        query += " LIMIT ?"
        cur.execute(query, (int(limit),))
    else:
        cur.execute(query)

    rows = cur.fetchall()
    logger.info("Iniciando sync manual. Pendientes leidos: %s", len(rows))

    enviadas = 0
    fallidas = 0

    for row in rows:
        rep_id = row["id"]
        payload = _to_payload(row)

        # Validacion minima antes de enviar
        if not payload["dni"]:
            fallidas += 1
            error_msg = "DNI vacio"
            cur.execute(
                """
                UPDATE reparaciones
                SET sync_attempts = sync_attempts + 1,
                    last_sync_error = ?,
                    sync_pending = 1
                WHERE id = ?
                """,
                (error_msg, rep_id),
            )
            conn.commit()
            logger.warning("Reparacion %s no enviada: %s", row["numero_orden"], error_msg)
            continue

        url = f"{config['api_base']}/api/reparaciones"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": config["api_key"],
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=config["timeout"])
            if 200 <= response.status_code < 300:
                enviadas += 1
                cur.execute(
                    """
                    UPDATE reparaciones
                    SET sync_pending = 0,
                        synced_at = ?,
                        last_sync_error = NULL,
                        external_id = ?
                    WHERE id = ?
                    """,
                    (datetime.now().isoformat(timespec="seconds"), payload["external_id"], rep_id),
                )
                conn.commit()
                logger.info("Reparacion %s sincronizada OK", row["numero_orden"])
            else:
                fallidas += 1
                error_msg = f"HTTP {response.status_code}: {response.text[:300]}"
                cur.execute(
                    """
                    UPDATE reparaciones
                    SET sync_attempts = sync_attempts + 1,
                        last_sync_error = ?,
                        sync_pending = 1
                    WHERE id = ?
                    """,
                    (error_msg, rep_id),
                )
                conn.commit()
                logger.error("Reparacion %s fallo sync: %s", row["numero_orden"], error_msg)
        except requests.Timeout:
            fallidas += 1
            error_msg = "Timeout al sincronizar"
            cur.execute(
                """
                UPDATE reparaciones
                SET sync_attempts = sync_attempts + 1,
                    last_sync_error = ?,
                    sync_pending = 1
                WHERE id = ?
                """,
                (error_msg, rep_id),
            )
            conn.commit()
            logger.error("Reparacion %s timeout", row["numero_orden"])
        except Exception as e:
            fallidas += 1
            error_msg = f"Excepcion: {str(e)[:250]}"
            cur.execute(
                """
                UPDATE reparaciones
                SET sync_attempts = sync_attempts + 1,
                    last_sync_error = ?,
                    sync_pending = 1
                WHERE id = ?
                """,
                (error_msg, rep_id),
            )
            conn.commit()
            logger.exception("Error inesperado en sync de %s", row["numero_orden"])

    conn.close()
    logger.info("Sync finalizado. Exito=%s Fallidas=%s", enviadas, fallidas)

    return {
        "ok": True,
        "enviadas": enviadas,
        "fallidas": fallidas,
        "total_procesadas": len(rows),
    }


if __name__ == "__main__":
    print(run_sync_once())

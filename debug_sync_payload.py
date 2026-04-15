"""
Diagnóstico de sincronización hacia API central.

Muestra el payload que se enviará y ejecuta un POST de prueba.

Uso:
    python debug_sync_payload.py
"""

import json
import os
import sqlite3

import requests

from sync_service import _load_config, _to_payload


def _connect(sqlite_path):
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn


def main():
    config = _load_config()

    print("== Config usada ==")
    print(f"CENTRAL_API_BASE: {config['api_base']}")
    print(f"SQLITE_PATH: {config['sqlite_path']}")
    print(f"TIMEOUT: {config['timeout']}")
    print(f"CENTRAL_API_KEY definida: {'SI' if bool(config['api_key']) else 'NO'}")

    if not config["api_base"] or not config["api_key"]:
        print("\nFaltan CENTRAL_API_BASE o CENTRAL_API_KEY en .env")
        return

    conn = _connect(config["sqlite_path"])
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, numero_orden, external_id, cliente_dni, dispositivo, modelo, problema, estado,
               fecha_creacion, fecha_entrega
        FROM reparaciones
        WHERE sync_pending = 1
        ORDER BY id ASC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        print("\nNo hay reparaciones pendientes para probar.")
        return

    payload = _to_payload(row)
    print("\n== Reparación seleccionada ==")
    print(f"id: {row['id']}")
    print(f"numero_orden: {row['numero_orden']}")

    print("\n== Payload a enviar ==")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    url = f"{config['api_base']}/api/reparaciones"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": config["api_key"],
    }

    print("\n== POST de prueba ==")
    print(f"URL: {url}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=config["timeout"])
        print(f"Status: {response.status_code}")
        print("Body:")
        print(response.text)
    except Exception as e:
        print(f"Error en request: {e}")


if __name__ == "__main__":
    main()

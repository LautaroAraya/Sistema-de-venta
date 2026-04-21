import os
import sqlite3
import json
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    firebase_admin = None
    credentials = None
    firestore = None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PANEL_DIR = os.path.join(BASE_DIR, "panel_tecnico")

# Carga variables desde .env (si existe) y .env.tecnico
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".env.tecnico"))

DB_PATH = os.getenv("SQLITE_PATH") or os.path.join(BASE_DIR, "database", "sistema_ventas.db")
APP_SECRET = os.getenv("TECNICO_APP_SECRET", "cambiar-este-secreto-en-produccion")
TOKEN_MAX_AGE = int(os.getenv("TECNICO_TOKEN_MAX_AGE_SECONDS", "28800"))
TECNICO_USER = os.getenv("TECNICO_USER", "tecnico")
TECNICO_PASS = os.getenv("TECNICO_PASS", "")
TECNICO_PASS_HASH = os.getenv("TECNICO_PASS_HASH", "")
ALLOW_CORS = os.getenv("TECNICO_ALLOW_CORS", "1") == "1"
EXPOSE_UNLOCK_FIELDS = os.getenv("TECNICO_EXPOSE_UNLOCK_FIELDS", "1") == "1"
DATA_BACKEND = (os.getenv("TECNICO_DATA_BACKEND", "sqlite") or "sqlite").strip().lower()
FIREBASE_COLLECTION = os.getenv("TECNICO_FIRESTORE_COLLECTION", "reparaciones_publicas")
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "").strip()

DB_FIRESTORE = None

serializer = URLSafeTimedSerializer(APP_SECRET, salt="tecnico-auth")

app = Flask(__name__)
if ALLOW_CORS:
    CORS(app)


def _buscar_credenciales_firebase(credentials_path):
    posibles_rutas = [
        credentials_path,
        os.path.join(BASE_DIR, credentials_path),
        os.path.join(os.getcwd(), credentials_path),
    ]

    for ruta in posibles_rutas:
        if ruta and os.path.exists(ruta):
            return ruta
    return None


def _inicializar_firestore_si_hace_falta():
    global DB_FIRESTORE

    if DATA_BACKEND != "firestore":
        return

    if firebase_admin is None:
        raise RuntimeError("Falta instalar firebase-admin")

    if DB_FIRESTORE is not None:
        return

    if not firebase_admin._apps:
        if FIREBASE_SERVICE_ACCOUNT_JSON:
            cred_dict = json.loads(FIREBASE_SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            cred_path = _buscar_credenciales_firebase(FIREBASE_CREDENTIALS_PATH)
            if not cred_path:
                raise FileNotFoundError("No se encontraron credenciales Firebase")
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

    DB_FIRESTORE = firestore.client()


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _token_for_user(username):
    return serializer.dumps({"username": username})


def _verify_token(token):
    return serializer.loads(token, max_age=TOKEN_MAX_AGE)


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"ok": False, "error": "Falta token Bearer"}), 401

        token = auth_header.replace("Bearer ", "", 1).strip()
        try:
            payload = _verify_token(token)
        except SignatureExpired:
            return jsonify({"ok": False, "error": "Token expirado"}), 401
        except BadSignature:
            return jsonify({"ok": False, "error": "Token invalido"}), 401

        request.current_user = payload.get("username", "")
        return fn(*args, **kwargs)

    return wrapper


def _validar_password(password_plano):
    if TECNICO_PASS_HASH:
        return check_password_hash(TECNICO_PASS_HASH, password_plano)
    if TECNICO_PASS:
        return password_plano == TECNICO_PASS
    return False


def _safe_reparacion_dict(row):
    data = {
        "id": row["id"],
        "numero_orden": row["numero_orden"],
        "cliente_nombre": row["cliente_nombre"],
        "cliente_telefono": row["cliente_telefono"],
        "cliente_email": row["cliente_email"],
        "cliente_dni": row["cliente_dni"],
        "dispositivo": row["dispositivo"],
        "modelo": row["modelo"],
        "numero_serie": row["numero_serie"],
        "problema": row["problema"],
        "sena": row["sena"],
        "total": row["total"],
        "estado": row["estado"],
        "fecha_creacion": row["fecha_creacion"],
        "fecha_entrega": row["fecha_entrega"],
        "observaciones": row["observaciones"],
    }

    if EXPOSE_UNLOCK_FIELDS:
        data["contrasena"] = row["contrasena"]
        data["patron"] = row["patron"]

    return data


def _safe_reparacion_from_firestore(doc_id, data):
    payload = {
        "id": str((data or {}).get("id") or doc_id),
        "numero_orden": (data or {}).get("numero_orden") or str(doc_id),
        "cliente_nombre": (data or {}).get("cliente_nombre") or "",
        "cliente_telefono": (data or {}).get("cliente_telefono") or "",
        "cliente_email": (data or {}).get("cliente_email") or "",
        "cliente_dni": (data or {}).get("cliente_dni") or "",
        "dispositivo": (data or {}).get("dispositivo") or "",
        "modelo": (data or {}).get("modelo") or "",
        "numero_serie": (data or {}).get("numero_serie") or "",
        "problema": (data or {}).get("falla") or (data or {}).get("problema") or "",
        "sena": (data or {}).get("sena") or "",
        "total": (data or {}).get("total") or "",
        "estado": (data or {}).get("estado") or "en_proceso",
        "fecha_creacion": (data or {}).get("fecha_creacion") or "",
        "fecha_entrega": (data or {}).get("fecha_entrega") or "",
        "observaciones": (data or {}).get("observaciones") or "",
    }

    if EXPOSE_UNLOCK_FIELDS:
        payload["contrasena"] = (data or {}).get("contrasena") or ""
        payload["patron"] = (data or {}).get("patron") or ""

    return payload


def _column_exists(conn, table_name, column_name):
    cur = conn.execute(f"PRAGMA table_info({table_name})")
    cols = [r[1] for r in cur.fetchall()]
    return column_name in cols


@app.route("/")
def home():
    return send_from_directory(PANEL_DIR, "index.html")


@app.route("/panel")
def panel_home():
    return send_from_directory(PANEL_DIR, "index.html")


@app.route("/panel/<path:filename>")
def panel_files(filename):
    return send_from_directory(PANEL_DIR, filename)


@app.route("/styles.css")
def panel_styles():
    return send_from_directory(PANEL_DIR, "styles.css")


@app.route("/app.js")
def panel_app_js():
    return send_from_directory(PANEL_DIR, "app.js")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "api_tecnico_remoto"})


@app.route("/api/auth/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if username != TECNICO_USER or not _validar_password(password):
        return jsonify({"ok": False, "error": "Credenciales invalidas"}), 401

    token = _token_for_user(username)
    return jsonify({
        "ok": True,
        "token": token,
        "token_type": "Bearer",
        "expires_in": TOKEN_MAX_AGE,
        "user": {"username": username, "rol": "tecnico"},
    })


@app.route("/api/tecnico/reparaciones", methods=["GET"])
@require_auth
def obtener_reparaciones_tecnico():
    estado = (request.args.get("estado") or "").strip()
    q = (request.args.get("q") or "").strip()

    try:
        limit = int(request.args.get("limit", "100"))
    except ValueError:
        limit = 100
    limit = max(1, min(500, limit))

    filters = []
    params = []

    if estado:
        filters.append("estado = ?")
        params.append(estado)

    if q:
        filters.append("(numero_orden LIKE ? OR cliente_nombre LIKE ? OR cliente_dni LIKE ? OR dispositivo LIKE ? OR modelo LIKE ?)")
        q_like = f"%{q}%"
        params.extend([q_like, q_like, q_like, q_like, q_like])

    where_clause = ""
    if filters:
        where_clause = " WHERE " + " AND ".join(filters)

    query = f"""
        SELECT
            id,
            numero_orden,
            cliente_nombre,
            cliente_telefono,
            cliente_email,
            cliente_dni,
            dispositivo,
            modelo,
            numero_serie,
            problema,
            contrasena,
            patron,
            sena,
            total,
            estado,
            fecha_creacion,
            fecha_entrega,
            observaciones
        FROM reparaciones
        {where_clause}
        ORDER BY fecha_creacion DESC
        LIMIT ?
    """
    params.append(limit)

    if DATA_BACKEND == "sqlite":
        conn = get_db_connection()
        rows = conn.execute(query, params).fetchall()
        conn.close()

        return jsonify({
            "ok": True,
            "cantidad": len(rows),
            "reparaciones": [_safe_reparacion_dict(r) for r in rows],
        })

    _inicializar_firestore_si_hace_falta()
    docs = DB_FIRESTORE.collection(FIREBASE_COLLECTION).stream()
    reparaciones = []
    q_norm = q.lower()

    for doc in docs:
        item = _safe_reparacion_from_firestore(doc.id, doc.to_dict() or {})

        if estado and item.get("estado") != estado:
            continue

        if q_norm:
            blob = " ".join(
                [
                    str(item.get("numero_orden", "")),
                    str(item.get("cliente_nombre", "")),
                    str(item.get("cliente_dni", "")),
                    str(item.get("dispositivo", "")),
                    str(item.get("modelo", "")),
                ]
            ).lower()
            if q_norm not in blob:
                continue

        reparaciones.append(item)

    reparaciones.sort(key=lambda x: x.get("fecha_creacion") or "", reverse=True)
    reparaciones = reparaciones[:limit]

    return jsonify({"ok": True, "cantidad": len(reparaciones), "reparaciones": reparaciones})


@app.route("/api/tecnico/reparaciones/orden/<numero_orden>", methods=["GET"])
@require_auth
def obtener_reparacion_por_orden(numero_orden):
    if DATA_BACKEND == "sqlite":
        conn = get_db_connection()
        row = conn.execute(
        """
        SELECT
            id,
            numero_orden,
            cliente_nombre,
            cliente_telefono,
            cliente_email,
            cliente_dni,
            dispositivo,
            modelo,
            numero_serie,
            problema,
            contrasena,
            patron,
            sena,
            total,
            estado,
            fecha_creacion,
            fecha_entrega,
            observaciones
        FROM reparaciones
        WHERE numero_orden = ?
        """,
        (numero_orden,),
        ).fetchone()
        conn.close()

        if not row:
            return jsonify({"ok": False, "error": "Reparacion no encontrada"}), 404

        return jsonify({"ok": True, "reparacion": _safe_reparacion_dict(row)})

    _inicializar_firestore_si_hace_falta()
    doc = DB_FIRESTORE.collection(FIREBASE_COLLECTION).document(str(numero_orden)).get()
    if not doc.exists:
        return jsonify({"ok": False, "error": "Reparacion no encontrada"}), 404

    return jsonify({"ok": True, "reparacion": _safe_reparacion_from_firestore(doc.id, doc.to_dict() or {})})


@app.route("/api/tecnico/reparaciones/<reparacion_id>/estado", methods=["PUT"])
@require_auth
def actualizar_estado(reparacion_id):
    data = request.get_json(silent=True) or {}
    nuevo_estado = (data.get("estado") or "").strip()

    if not nuevo_estado:
        return jsonify({"ok": False, "error": "El campo estado es obligatorio"}), 400

    estados_validos = {"en_proceso", "en_espera_retiro", "retirado"}
    if nuevo_estado not in estados_validos:
        return jsonify({"ok": False, "error": "Estado invalido"}), 400

    if DATA_BACKEND == "sqlite":
        conn = get_db_connection()

        try:
            reparacion_id_int = int(reparacion_id)
        except ValueError:
            conn.close()
            return jsonify({"ok": False, "error": "ID invalido para SQLite"}), 400

        existe = conn.execute("SELECT id FROM reparaciones WHERE id = ?", (reparacion_id_int,)).fetchone()
        if not existe:
            conn.close()
            return jsonify({"ok": False, "error": "Reparacion no encontrada"}), 404

        set_parts = ["estado = ?"]
        params = [nuevo_estado]

        if _column_exists(conn, "reparaciones", "sync_pending"):
            set_parts.append("sync_pending = 1")
        if _column_exists(conn, "reparaciones", "last_sync_error"):
            set_parts.append("last_sync_error = NULL")

        params.append(reparacion_id_int)
        sql = f"UPDATE reparaciones SET {', '.join(set_parts)} WHERE id = ?"
        conn.execute(sql, params)
        conn.commit()
        conn.close()

        return jsonify({"ok": True, "mensaje": "Estado actualizado"})

    _inicializar_firestore_si_hace_falta()
    ref = DB_FIRESTORE.collection(FIREBASE_COLLECTION).document(str(reparacion_id))
    doc = ref.get()
    if not doc.exists:
        return jsonify({"ok": False, "error": "Reparacion no encontrada"}), 404

    ref.update({"estado": nuevo_estado})
    return jsonify({"ok": True, "mensaje": "Estado actualizado"})


if __name__ == "__main__":
    if DATA_BACKEND == "sqlite" and not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"No se encontro la base de datos en: {DB_PATH}")

    if DATA_BACKEND == "firestore":
        _inicializar_firestore_si_hace_falta()

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")), debug=False)

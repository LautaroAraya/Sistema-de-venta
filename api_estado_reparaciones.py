"""
API intermedia para consultar estado de reparaciones por DNI.

Uso:
    pip install flask firebase-admin
    python api_estado_reparaciones.py

Endpoint:
    GET /api/reparaciones/estado?dni=12345678

Opcional:
    Definir WEB_API_KEY en variables de entorno y enviar header X-API-Key.
"""

import os
from datetime import datetime

from flask import Flask, jsonify, request

import firebase_admin
from firebase_admin import credentials, firestore
from sync_service import run_sync_once, get_sync_status

try:
    from firebase_config import REPARACIONES_PUBLICAS_COLLECTION
except ImportError:
    REPARACIONES_PUBLICAS_COLLECTION = "reparaciones_publicas"


app = Flask(__name__)
DB = None
WEB_API_KEY = os.environ.get("WEB_API_KEY", "").strip()


def _buscar_credenciales(credentials_path="serviceAccountKey.json"):
    posibles_rutas = [
        credentials_path,
        os.path.join(os.path.dirname(__file__), credentials_path),
        os.path.join(os.getcwd(), credentials_path),
        os.environ.get("FIREBASE_CREDENTIALS_PATH", ""),
    ]

    for ruta in posibles_rutas:
        if ruta and os.path.exists(ruta):
            return ruta
    return None


def inicializar_firestore():
    global DB

    if DB is not None:
        return

    cred_path = _buscar_credenciales()
    if not cred_path:
        raise FileNotFoundError("No se encontro serviceAccountKey.json")

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    DB = firestore.client()


def _respuesta(datos, status=200):
    response = jsonify(datos)
    response.status_code = status
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    return response


def _validar_api_key():
    if not WEB_API_KEY:
        return True
    return request.headers.get("X-API-Key", "").strip() == WEB_API_KEY


@app.route("/api/reparaciones/estado", methods=["GET", "OPTIONS"])
def estado_reparacion_por_dni():
    if request.method == "OPTIONS":
        return _respuesta({"ok": True})

    if not _validar_api_key():
        return _respuesta({"ok": False, "error": "No autorizado"}, status=401)

    dni = (request.args.get("dni") or "").strip()
    if not dni:
        return _respuesta({"ok": False, "error": "Parametro dni obligatorio"}, status=400)

    try:
        inicializar_firestore()
        docs = DB.collection(REPARACIONES_PUBLICAS_COLLECTION).where("cliente_dni", "==", dni).stream()

        reparaciones = []
        for doc in docs:
            data = doc.to_dict() or {}
            reparaciones.append({
                "numero_orden": data.get("numero_orden", ""),
                "equipo": data.get("equipo", ""),
                "falla": data.get("falla", ""),
                "dispositivo": data.get("dispositivo", ""),
                "modelo": data.get("modelo", ""),
                "estado": data.get("estado", ""),
                "estado_texto": data.get("estado_texto", ""),
                "fecha_creacion": data.get("fecha_creacion", ""),
                "fecha_entrega": data.get("fecha_entrega", ""),
                "fecha_actualizacion": data.get("fecha_actualizacion", ""),
            })

        reparaciones.sort(key=lambda x: x.get("fecha_actualizacion") or "", reverse=True)

        return _respuesta({
            "ok": True,
            "dni": dni,
            "cantidad": len(reparaciones),
            "reparaciones": reparaciones,
            "timestamp": datetime.now().isoformat(),
        })
    except Exception as e:
        return _respuesta({"ok": False, "error": str(e)}, status=500)


@app.route("/health", methods=["GET"])
def health():
    return _respuesta({"ok": True, "service": "api_estado_reparaciones"})


@app.route("/sync-now", methods=["POST", "OPTIONS"])
def sync_now():
    if request.method == "OPTIONS":
        return _respuesta({"ok": True})

    if not _validar_api_key():
        return _respuesta({"ok": False, "error": "No autorizado"}, status=401)

    payload = request.get_json(silent=True) or {}
    limit = payload.get("limit")

    result = run_sync_once(limit=limit)
    status_code = 200 if result.get("ok") else 500
    return _respuesta(result, status=status_code)


@app.route("/sync-status", methods=["GET"])
def sync_status():
    if not _validar_api_key():
        return _respuesta({"ok": False, "error": "No autorizado"}, status=401)

    try:
        status = get_sync_status()
        return _respuesta({"ok": True, **status})
    except Exception as e:
        return _respuesta({"ok": False, "error": str(e)}, status=500)


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=puerto, debug=False)

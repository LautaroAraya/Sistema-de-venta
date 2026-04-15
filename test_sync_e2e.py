"""
Prueba end-to-end para sincronizacion.

Requisitos:
1) Tener corriendo api_estado_reparaciones.py localmente.
2) Configurar .env con CENTRAL_API_BASE y CENTRAL_API_KEY.

Uso:
    python test_sync_e2e.py
"""

import os
import requests


def _load_dotenv(dotenv_path=".env"):
    if not os.path.exists(dotenv_path):
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main():
    _load_dotenv()

    api_base = os.environ.get("LOCAL_SYNC_API", "http://127.0.0.1:8080").rstrip("/")
    web_api_key = os.environ.get("WEB_API_KEY", "").strip()

    headers = {}
    if web_api_key:
        headers["X-API-Key"] = web_api_key

    print("== Estado antes ==")
    r1 = requests.get(f"{api_base}/sync-status", headers=headers, timeout=10)
    print(r1.status_code, r1.text)

    print("\n== Ejecutando sync-now ==")
    r2 = requests.post(f"{api_base}/sync-now", json={}, headers=headers, timeout=60)
    print(r2.status_code, r2.text)

    print("\n== Estado despues ==")
    r3 = requests.get(f"{api_base}/sync-status", headers=headers, timeout=10)
    print(r3.status_code, r3.text)


if __name__ == "__main__":
    main()

"""
Sincronización de reparaciones a Firestore para consulta pública en web.
"""

import os
from datetime import datetime

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    firebase_admin = None
    credentials = None
    firestore = None

try:
    from firebase_config import REPARACIONES_PUBLICAS_COLLECTION
except ImportError:
    REPARACIONES_PUBLICAS_COLLECTION = "reparaciones_publicas"


class ReparacionesSync:
    """Sincroniza reparaciones con una colección pública en Firestore."""

    def __init__(self, credentials_path="serviceAccountKey.json"):
        self.credentials_path = credentials_path
        self.db = None
        self.enabled = self._inicializar_firebase()

    def _inicializar_firebase(self):
        if firebase_admin is None:
            return False

        try:
            if not firebase_admin._apps:
                posibles_rutas = [
                    self.credentials_path,
                    os.path.join(os.path.dirname(__file__), "..", self.credentials_path),
                    os.path.join(os.getcwd(), self.credentials_path),
                    os.environ.get("FIREBASE_CREDENTIALS_PATH", "")
                ]

                credentials_file = None
                for ruta in posibles_rutas:
                    if ruta and os.path.exists(ruta):
                        credentials_file = ruta
                        break

                if not credentials_file:
                    return False

                cred = credentials.Certificate(credentials_file)
                firebase_admin.initialize_app(cred)

            self.db = firestore.client()
            return True
        except Exception:
            return False

    def _doc_from_reparacion(self, reparacion):
        estado_map = {
            "en_proceso": "En reparacion",
            "en_espera_retiro": "En espera de retiro",
            "retirado": "Retirado",
        }

        dispositivo = (reparacion.get("dispositivo") or "").strip()
        modelo = (reparacion.get("modelo") or "").strip()
        equipo = dispositivo if not modelo else f"{dispositivo} {modelo}"

        return {
            "numero_orden": reparacion.get("numero_orden"),
            "cliente_dni": (reparacion.get("cliente_dni") or "").strip(),
            "cliente_nombre": reparacion.get("cliente_nombre") or "",
            "cliente_telefono": reparacion.get("cliente_telefono") or "",
            "dispositivo": dispositivo,
            "modelo": modelo,
            "equipo": equipo,
            "falla": (reparacion.get("problema") or "").strip(),
            "estado": reparacion.get("estado") or "en_proceso",
            "estado_texto": estado_map.get(reparacion.get("estado"), "En reparacion"),
            "fecha_creacion": reparacion.get("fecha_creacion") or "",
            "fecha_entrega": reparacion.get("fecha_entrega") or "",
            "fecha_actualizacion": datetime.now().isoformat(),
        }

    def upsert_reparacion(self, reparacion):
        """Crea o actualiza una reparación pública en Firestore."""
        if not self.enabled or not self.db:
            return False, "Sincronización Firebase deshabilitada"

        numero_orden = (reparacion or {}).get("numero_orden")
        if not numero_orden:
            return False, "Reparación sin número de orden"

        try:
            payload = self._doc_from_reparacion(reparacion)
            self.db.collection(REPARACIONES_PUBLICAS_COLLECTION).document(str(numero_orden)).set(payload)
            return True, "Sincronizado"
        except Exception as e:
            return False, str(e)

    def delete_reparacion(self, numero_orden):
        """Elimina una reparación pública en Firestore."""
        if not self.enabled or not self.db:
            return False, "Sincronización Firebase deshabilitada"

        if not numero_orden:
            return False, "Número de orden inválido"

        try:
            self.db.collection(REPARACIONES_PUBLICAS_COLLECTION).document(str(numero_orden)).delete()
            return True, "Eliminado"
        except Exception as e:
            return False, str(e)

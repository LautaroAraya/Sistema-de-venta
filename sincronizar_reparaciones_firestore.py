"""
Sincroniza todas las reparaciones existentes a Firestore.

Uso:
    python sincronizar_reparaciones_firestore.py
"""

from database.db_manager import DatabaseManager
from models.reparacion import Reparacion
from utils.reparaciones_sync import ReparacionesSync


def main():
    db_manager = DatabaseManager()
    reparacion_model = Reparacion(db_manager)
    sync = ReparacionesSync()

    if not sync.enabled:
        print("No se pudo inicializar Firebase. Verifica serviceAccountKey.json")
        return

    reparaciones = reparacion_model.obtener_reparaciones()
    total = len(reparaciones)
    ok = 0

    for rep in reparaciones:
        estado, _msg = sync.upsert_reparacion(rep)
        if estado:
            ok += 1

    print(f"Sincronizadas: {ok}/{total}")


if __name__ == "__main__":
    main()

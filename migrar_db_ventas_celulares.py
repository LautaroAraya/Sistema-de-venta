import os
import sqlite3
import shutil
from datetime import datetime


def _resolve_db_path(base_dir):
    primary = os.path.join(base_dir, "database", "sistema_ventas.db")
    if os.path.exists(primary):
        return primary

    fallback = os.path.join(base_dir, "sistema_ventas.db")
    if os.path.exists(fallback):
        return fallback

    return primary


def _backup_db(db_path, base_dir):
    backup_dir = os.path.join(base_dir, "database", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"sistema_ventas_{timestamp}.db")
    shutil.copy2(db_path, backup_path)
    return backup_path


def _get_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [row[1] for row in cursor.fetchall()]


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = _resolve_db_path(base_dir)

    if not os.path.exists(db_path):
        print(f"ERROR: No se encontro la base de datos en: {db_path}")
        return 1

    conn = None
    try:
        backup_path = _backup_db(db_path, base_dir)
        print(f"Backup creado: {backup_path}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ventas_celulares'")
        if not cursor.fetchone():
            print("ERROR: No existe la tabla ventas_celulares")
            return 1

        columnas = set(_get_columns(cursor, "ventas_celulares"))

        cambios = []
        if "fecha_pago_final" not in columnas:
            cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN fecha_pago_final TIMESTAMP")
            cambios.append("fecha_pago_final")
        if "medio_pago_final" not in columnas:
            cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN medio_pago_final TEXT")
            cambios.append("medio_pago_final")
        if "monto_pago_final" not in columnas:
            cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN monto_pago_final REAL DEFAULT 0")
            cambios.append("monto_pago_final")
        if "recargo_tarjeta" not in columnas:
            cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN recargo_tarjeta REAL DEFAULT 0")
            cambios.append("recargo_tarjeta")

        if cambios:
            conn.commit()
            print("Migracion OK. Columnas agregadas:")
            for col in cambios:
                print(f"- {col}")
        else:
            print("No hay cambios. La tabla ya tiene las columnas necesarias.")

        return 0
    except Exception as exc:
        if conn:
            conn.rollback()
        print(f"ERROR: {exc}")
        return 1
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    raise SystemExit(main())

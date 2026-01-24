import sqlite3
import os

def ejecutar_migracion(base_dir):
    # Usamos BASE_DIR para asegurar que apunte a la DB correcta
    db_path = os.path.join(base_dir, 'sistema_ventas.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    def add_column_if_not_exists(table, column, coltype):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [info[1] for info in cursor.fetchall()]
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")

    try:
        add_column_if_not_exists('ventas', 'metodo_pago', 'TEXT DEFAULT "Efectivo"')
        add_column_if_not_exists('ventas', 'recargo', 'REAL DEFAULT 0')
        conn.commit()
        print('Migración de base de datos completada exitosamente.')
    except Exception as e:
        print(f"Error durante la migración: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Esto permite que el script siga funcionando solo si lo ejecutas manualmente
    ejecutar_migracion(".")

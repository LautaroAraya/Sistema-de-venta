import sqlite3
import os

# Ruta absoluta a la base de datos
DB_PATH = os.path.join(os.path.dirname(__file__), 'sistema_ventas.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def add_column_if_not_exists(table, column, coltype):
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")

add_column_if_not_exists('ventas', 'metodo_pago', 'TEXT DEFAULT "Efectivo"')
add_column_if_not_exists('ventas', 'recargo', 'REAL DEFAULT 0')

conn.commit()
conn.close()
print('Migración completada.')

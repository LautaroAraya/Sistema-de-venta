import sqlite3

conn = sqlite3.connect('sistema_ventas.db')
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

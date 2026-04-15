"""
Completa cliente_dni en reparaciones cuando está vacío,
usando el valor de numero_serie como fuente.

Uso:
    python migrar_dni_desde_numero_serie.py
"""

from database.db_manager import DatabaseManager


def main():
    db = DatabaseManager()
    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM reparaciones
        WHERE (cliente_dni IS NULL OR TRIM(cliente_dni) = '')
          AND numero_serie IS NOT NULL
          AND TRIM(numero_serie) <> ''
        """
    )
    pendientes = cur.fetchone()[0]

    cur.execute(
        """
        UPDATE reparaciones
        SET cliente_dni = TRIM(numero_serie),
            sync_pending = 1,
            synced_at = NULL,
            last_sync_error = NULL
        WHERE (cliente_dni IS NULL OR TRIM(cliente_dni) = '')
          AND numero_serie IS NOT NULL
          AND TRIM(numero_serie) <> ''
        """
    )
    actualizadas = cur.rowcount
    conn.commit()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM reparaciones
        WHERE cliente_dni IS NULL OR TRIM(cliente_dni) = ''
        """
    )
    sin_dni = cur.fetchone()[0]

    db.close()

    print(f"Pendientes detectadas: {pendientes}")
    print(f"Reparaciones actualizadas: {actualizadas}")
    print(f"Reparaciones aún sin DNI: {sin_dni}")


if __name__ == "__main__":
    main()

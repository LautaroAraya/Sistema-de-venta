"""
Script para resetear los IDs de categorías a valores secuenciales
"""

import sys
import io

# Forzar UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from database.db_manager import DatabaseManager
from models.categoria import Categoria
import sqlite3

def resetear_categorias():
    """Resetear IDs de categorías y insertarlas en orden"""
    print("Reseteando categorías en la base de datos...")
    
    db = DatabaseManager()
    categoria_model = Categoria(db)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Eliminar todas las categorías
        print("\nEliminando categorías...")
        cursor.execute('DELETE FROM categorias')
        conn.commit()
        print("✓ Categorías eliminadas")
        
        # Resetear el contador de secuencia en SQLite
        print("Reseteando contador de IDs...")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='categorias'")
        conn.commit()
        print("✓ Contador reseteado")
        
        # Insertar categorías en orden alfabético
        print("\nInsertando categorías en orden...")
        categorias_ordenadas = [
            ("Accesorios", "Accesorios para celular y otros dispositivos"),
            ("Auriculares", "Auriculares y headsets"),
            ("Cámaras de Seguridad", "Cámaras de vigilancia y seguridad"),
            ("Cargadores", "Cargadores para dispositivos móviles"),
            ("Focos LED", "Focos de luz LED"),
            ("Otros", "Otros productos"),
            ("Parlantes", "Parlantes para música y audio"),
            ("Pendrives", "Memorias USB y pendrives"),
            ("Relojes Smart", "Relojes inteligentes"),
            ("Tiras LED", "Tiras de luz LED decorativas"),
        ]
        
        for nombre, desc in categorias_ordenadas:
            exito, msg = categoria_model.crear_categoria(nombre, desc)
            print(f"  ✓ {nombre}")
        
        # Verificar los IDs
        print("\nVerificando IDs asignados:")
        cursor.execute('SELECT id, nombre FROM categorias ORDER BY id')
        for row in cursor.fetchall():
            print(f"  ID {row[0]}: {row[1]}")
        
        print("\n✅ Categorías reseteadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error al resetear categorías: {str(e)}")
        conn.rollback()
        return False
    
    return True

if __name__ == "__main__":
    resetear_categorias()
    print("\nProceso completado. Cierra y reinicia la aplicación.")

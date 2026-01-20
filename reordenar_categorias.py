"""
Script para reordenar las categorías en la base de datos
"""

from database.db_manager import DatabaseManager
from models.categoria import Categoria

def reordenar_categorias():
    """Limpiar categorías y insertarlas en orden"""
    print("Reordenando categorías en la base de datos...")
    
    db = DatabaseManager()
    categoria_model = Categoria(db)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Eliminar categorías
        print("\nEliminando categorías...")
        cursor.execute('DELETE FROM categorias')
        conn.commit()
        print("✓ Categorías eliminadas")
        
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
        
        print("\n✅ Categorías reordenadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error al reordenar categorías: {str(e)}")
        conn.rollback()
        return False
    
    return True

if __name__ == "__main__":
    reordenar_categorias()
    print("\nProceso completado. Cierra y reinicia la aplicación.")

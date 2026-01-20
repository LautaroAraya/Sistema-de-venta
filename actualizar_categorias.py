"""
Script para limpiar las categorías antiguas e insertar las nuevas
Ejecutar después de cambiar las categorías
"""

from database.db_manager import DatabaseManager
from models.categoria import Categoria

def actualizar_categorias():
    """Limpiar categorías antiguas e insertar nuevas"""
    print("Actualizando categorías en la base de datos...")
    
    db = DatabaseManager()
    categoria_model = Categoria(db)
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        # Eliminar categorías antiguas
        print("\nEliminando categorías antiguas...")
        cursor.execute('DELETE FROM categorias')
        conn.commit()
        print("✓ Categorías antiguas eliminadas")
        
        # Insertar nuevas categorías
        print("\nInsertando nuevas categorías...")
        nuevas_categorias = [
            ("Accesorios", "Accesorios para celular y otros dispositivos"),
            ("Parlantes", "Parlantes para música y audio"),
            ("Auriculares", "Auriculares y headsets"),
            ("Relojes Smart", "Relojes inteligentes"),
            ("Focos LED", "Focos de luz LED"),
            ("Tiras LED", "Tiras de luz LED decorativas"),
            ("Pendrives", "Memorias USB y pendrives"),
            ("Cámaras de Seguridad", "Cámaras de vigilancia y seguridad"),
            ("Cargadores", "Cargadores para dispositivos móviles"),
            ("Otros", "Otros productos")
        ]
        
        for nombre, desc in nuevas_categorias:
            exito, msg = categoria_model.crear_categoria(nombre, desc)
            print(f"  ✓ {nombre}")
        
        print("\n✅ Categorías actualizadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error al actualizar categorías: {str(e)}")
        conn.rollback()
        return False
    
    return True

if __name__ == "__main__":
    actualizar_categorias()
    print("\nProceso completado. Cierra el programa y reinicia para ver los cambios.")

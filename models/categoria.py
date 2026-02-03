from database.db_manager import DatabaseManager
from datetime import datetime

class Categoria:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def crear_categoria(self, nombre, descripcion):
        """Crear nueva categoría"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO categorias (nombre, descripcion, fecha_creacion)
                VALUES (?, ?, ?)
            ''', (nombre, descripcion, fecha_actual))
            conn.commit()
            return True, "Categoría creada exitosamente"
        except Exception as e:
            return False, f"Error al crear categoría: {str(e)}"
    
    def listar_categorias(self, activos_solo=True):
        """Listar categorías"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT id, nombre, descripcion FROM categorias'
        
        if activos_solo:
            query += ' WHERE activo = 1'
        
        query += ' ORDER BY nombre'
        
        cursor.execute(query)
        return cursor.fetchall()
    
    def eliminar_categoria(self, categoria_id):
        """Eliminar (desactivar) categoría"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE categorias
            SET activo = 0
            WHERE id = ?
        ''', (categoria_id,))
        
        conn.commit()
        return True, "Categoría eliminada exitosamente"

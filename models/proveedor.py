from database.db_manager import DatabaseManager

class Proveedor:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def crear_proveedor(self, nombre, contacto, telefono, email, direccion):
        """Crear nuevo proveedor"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO proveedores (nombre, contacto, telefono, email, direccion)
                VALUES (?, ?, ?, ?, ?)
            ''', (nombre, contacto, telefono, email, direccion))
            conn.commit()
            return True, "Proveedor creado exitosamente"
        except Exception as e:
            return False, f"Error al crear proveedor: {str(e)}"
    
    def actualizar_proveedor(self, proveedor_id, nombre, contacto, telefono, email, direccion):
        """Actualizar proveedor existente"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE proveedores
                SET nombre = ?, contacto = ?, telefono = ?, email = ?, direccion = ?
                WHERE id = ?
            ''', (nombre, contacto, telefono, email, direccion, proveedor_id))
            conn.commit()
            return True, "Proveedor actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar proveedor: {str(e)}"
    
    def listar_proveedores(self, activos_solo=True):
        """Listar proveedores"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, nombre, contacto, telefono, email, direccion, fecha_registro
            FROM proveedores
        '''
        
        if activos_solo:
            query += ' WHERE activo = 1'
        
        query += ' ORDER BY nombre'
        
        cursor.execute(query)
        return cursor.fetchall()
    
    def obtener_proveedor_por_id(self, proveedor_id):
        """Obtener proveedor por ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nombre, contacto, telefono, email, direccion
            FROM proveedores
            WHERE id = ? AND activo = 1
        ''', (proveedor_id,))
        
        return cursor.fetchone()
    
    def eliminar_proveedor(self, proveedor_id):
        """Eliminar (desactivar) proveedor"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE proveedores
            SET activo = 0
            WHERE id = ?
        ''', (proveedor_id,))
        
        conn.commit()
        return True, "Proveedor eliminado exitosamente"

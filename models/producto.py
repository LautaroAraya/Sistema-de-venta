from database.db_manager import DatabaseManager
from datetime import datetime

class Producto:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def crear_producto(self, codigo, nombre, descripcion, categoria_id, precio, stock, proveedor_id):
        """Crear nuevo producto"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO productos (codigo, nombre, descripcion, categoria_id, precio, stock, proveedor_id, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (codigo, nombre, descripcion, categoria_id, precio, stock, proveedor_id, fecha_actual))
            conn.commit()
            return True, "Producto creado exitosamente"
        except Exception as e:
            return False, f"Error al crear producto: {str(e)}"
    
    def actualizar_producto(self, producto_id, codigo, nombre, descripcion, categoria_id, precio, stock, proveedor_id):
        """Actualizar producto existente"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE productos
                SET codigo = ?, nombre = ?, descripcion = ?, categoria_id = ?, 
                    precio = ?, stock = ?, proveedor_id = ?
                WHERE id = ?
            ''', (codigo, nombre, descripcion, categoria_id, precio, stock, proveedor_id, producto_id))
            conn.commit()
            return True, "Producto actualizado exitosamente"
        except Exception as e:
            return False, f"Error al actualizar producto: {str(e)}"
    
    def listar_productos(self, activos_solo=True):
        """Listar productos"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT p.id, p.codigo, p.nombre, p.descripcion, c.nombre as categoria, 
                   p.precio, p.stock, pr.nombre as proveedor
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
        '''
        
        if activos_solo:
            query += ' WHERE p.activo = 1'
        
        query += ' ORDER BY p.nombre'
        
        cursor.execute(query)
        return cursor.fetchall()
    
    def buscar_producto(self, termino):
        """Buscar productos por código o nombre"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.codigo, p.nombre, p.descripcion, c.nombre as categoria, 
                   p.precio, p.stock, pr.nombre as proveedor
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            LEFT JOIN proveedores pr ON p.proveedor_id = pr.id
            WHERE p.activo = 1 AND (p.codigo LIKE ? OR p.nombre LIKE ?)
            ORDER BY p.nombre
        ''', (f'%{termino}%', f'%{termino}%'))
        
        return cursor.fetchall()
    
    def obtener_producto_por_id(self, producto_id):
        """Obtener producto por ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, codigo, nombre, descripcion, categoria_id, precio, stock, proveedor_id
            FROM productos
            WHERE id = ? AND activo = 1
        ''', (producto_id,))
        
        return cursor.fetchone()
    
    def actualizar_stock(self, producto_id, cantidad):
        """Actualizar stock de producto"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE productos
            SET stock = stock - ?
            WHERE id = ?
        ''', (cantidad, producto_id))
        
        conn.commit()
    
    def eliminar_producto(self, producto_id):
        """Eliminar (desactivar) producto"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE productos
            SET activo = 0
            WHERE id = ?
        ''', (producto_id,))
        
        conn.commit()
        return True, "Producto eliminado exitosamente"

from database.db_manager import DatabaseManager
from datetime import datetime
import random

class Venta:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def generar_numero_factura(self):
        """Generar número de factura único"""
        fecha = datetime.now().strftime('%Y%m%d')
        random_num = random.randint(1000, 9999)
        return f"FAC-{fecha}-{random_num}"
    
    def crear_venta(self, usuario_id, cliente_nombre, cliente_documento, items, metodo_pago="Efectivo", recargo=0.0):
        """
        Crear nueva venta con sus detalles
        items = [{
            'producto_id': int,
            'cantidad': int,
            'precio_unitario': float,
            'descuento_porcentaje': float
        }]
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Generar número de factura
            numero_factura = self.generar_numero_factura()
            
            # Calcular totales
            subtotal = 0
            descuento_total = 0
            
            for item in items:
                item_subtotal = item['cantidad'] * item['precio_unitario']
                item_descuento = item_subtotal * (item.get('descuento_porcentaje', 0) / 100)
                subtotal += item_subtotal
                descuento_total += item_descuento
            
            total = subtotal - descuento_total
            
            # Insertar venta
            cursor.execute('''
                INSERT INTO ventas (numero_factura, usuario_id, cliente_nombre, cliente_documento, 
                                   subtotal, descuento_total, total, metodo_pago, recargo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (numero_factura, usuario_id, cliente_nombre, cliente_documento, 
                  subtotal, descuento_total, total, metodo_pago, recargo))
            
            venta_id = cursor.lastrowid
            
            # Insertar detalles de venta
            for item in items:
                item_subtotal = item['cantidad'] * item['precio_unitario']
                descuento_porcentaje = item.get('descuento_porcentaje', 0)
                descuento_monto = item_subtotal * (descuento_porcentaje / 100)
                
                cursor.execute('''
                    INSERT INTO detalles_venta (venta_id, producto_id, cantidad, precio_unitario, 
                                               descuento_porcentaje, descuento_monto, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (venta_id, item['producto_id'], item['cantidad'], item['precio_unitario'],
                      descuento_porcentaje, descuento_monto, item_subtotal - descuento_monto))
                
                # Actualizar stock
                cursor.execute('''
                    UPDATE productos
                    SET stock = stock - ?
                    WHERE id = ?
                ''', (item['cantidad'], item['producto_id']))
            
            conn.commit()
            return True, numero_factura, venta_id
        
        except Exception as e:
            conn.rollback()
            return False, f"Error al crear venta: {str(e)}", None
    
    def obtener_venta_por_id(self, venta_id):
        """Obtener información completa de una venta"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Obtener información de la venta
        cursor.execute('''
            SELECT v.id, v.numero_factura, v.cliente_nombre, v.cliente_documento,
                   v.subtotal, v.descuento_total, v.total, v.fecha_venta,
                   u.nombre_completo as vendedor, v.metodo_pago, v.recargo
            FROM ventas v
            JOIN usuarios u ON v.usuario_id = u.id
            WHERE v.id = ?
        ''', (venta_id,))
        
        venta = cursor.fetchone()
        
        if not venta:
            return None
        
        # Obtener detalles de la venta
        cursor.execute('''
            SELECT dv.cantidad, dv.precio_unitario, dv.descuento_porcentaje, 
                   dv.descuento_monto, dv.subtotal, p.nombre as producto
            FROM detalles_venta dv
            JOIN productos p ON dv.producto_id = p.id
            WHERE dv.venta_id = ?
        ''', (venta_id,))
        
        detalles = cursor.fetchall()
        
        return {
            'venta': venta,
            'detalles': detalles
        }
    
    def listar_ventas(self, fecha_inicio=None, fecha_fin=None, usuario_id=None):
        """Listar ventas con filtros opcionales"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT v.id, v.numero_factura, v.cliente_nombre, v.total, v.fecha_venta,
                   u.nombre_completo as vendedor
            FROM ventas v
            JOIN usuarios u ON v.usuario_id = u.id
            WHERE 1=1
        '''
        
        params = []
        
        if fecha_inicio:
            query += ' AND DATE(v.fecha_venta) >= ?'
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += ' AND DATE(v.fecha_venta) <= ?'
            params.append(fecha_fin)
        
        if usuario_id:
            query += ' AND v.usuario_id = ?'
            params.append(usuario_id)
        
        query += ' ORDER BY v.fecha_venta DESC'
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def obtener_estadisticas(self, fecha_inicio=None, fecha_fin=None):
        """Obtener estadísticas de ventas"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                COUNT(*) as total_ventas,
                COALESCE(SUM(total), 0) as total_ingresos,
                COALESCE(AVG(total), 0) as promedio_venta
            FROM ventas
            WHERE 1=1
        '''
        
        params = []
        
        if fecha_inicio:
            query += ' AND DATE(fecha_venta) >= ?'
            params.append(fecha_inicio)
        
        if fecha_fin:
            query += ' AND DATE(fecha_venta) <= ?'
            params.append(fecha_fin)
        
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def eliminar_venta(self, venta_id):
        """
        Eliminar una venta y sus detalles asociados
        Devuelve los productos al stock
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Obtener detalles de la venta para devolver el stock
            cursor.execute('''
                SELECT producto_id, cantidad
                FROM detalles_venta
                WHERE venta_id = ?
            ''', (venta_id,))
            
            detalles = cursor.fetchall()
            
            # Devolver stock de cada producto
            for detalle in detalles:
                producto_id, cantidad = detalle
                cursor.execute('''
                    UPDATE productos
                    SET stock = stock + ?
                    WHERE id = ?
                ''', (cantidad, producto_id))
            
            # Eliminar detalles de venta
            cursor.execute('''
                DELETE FROM detalles_venta
                WHERE venta_id = ?
            ''', (venta_id,))
            
            # Eliminar venta
            cursor.execute('''
                DELETE FROM ventas
                WHERE id = ?
            ''', (venta_id,))
            
            conn.commit()
            return True, "Venta eliminada correctamente. El stock ha sido actualizado."
        
        except Exception as e:
            conn.rollback()
            return False, f"Error al eliminar venta: {str(e)}"

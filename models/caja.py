from datetime import datetime

class Caja:
    def __init__(self, db_manager):
        self.db = db_manager
        self._crear_tabla()
    
    def _crear_tabla(self):
        """Crear tabla de cajas si no existe"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cajas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                monto_inicial REAL NOT NULL,
                monto_final REAL,
                ventas_efectivo REAL DEFAULT 0,
                ventas_tarjeta REAL DEFAULT 0,
                reparaciones_efectivo REAL DEFAULT 0,
                reparaciones_tarjeta REAL DEFAULT 0,
                otros_ingresos REAL DEFAULT 0,
                otros_egresos REAL DEFAULT 0,
                observaciones TEXT,
                fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_cierre TIMESTAMP,
                estado TEXT DEFAULT 'abierta' CHECK(estado IN ('abierta', 'cerrada')),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
        ''')
        conn.commit()
    
    def abrir_caja(self, usuario_id, monto_inicial, observaciones=''):
        """Abrir una nueva caja"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Verificar que no haya una caja abierta
        cursor.execute('SELECT id FROM cajas WHERE estado = ? ORDER BY id DESC LIMIT 1', ('abierta',))
        caja_abierta = cursor.fetchone()
        
        if caja_abierta:
            return False, "Ya existe una caja abierta. Debe cerrarla antes de abrir una nueva."
        
        try:
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO cajas (usuario_id, monto_inicial, observaciones, fecha_apertura)
                VALUES (?, ?, ?, ?)
            ''', (usuario_id, monto_inicial, observaciones, fecha_actual))
            conn.commit()
            return True, "Caja abierta exitosamente"
        except Exception as e:
            return False, f"Error al abrir caja: {str(e)}"
    
    def cerrar_caja(self, caja_id, monto_final, ventas_efectivo=0, ventas_tarjeta=0, 
                    reparaciones_efectivo=0, reparaciones_tarjeta=0, 
                    otros_ingresos=0, otros_egresos=0, observaciones=''):
        """Cerrar una caja existente"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE cajas SET 
                    monto_final = ?,
                    ventas_efectivo = ?,
                    ventas_tarjeta = ?,
                    reparaciones_efectivo = ?,
                    reparaciones_tarjeta = ?,
                    otros_ingresos = ?,
                    otros_egresos = ?,
                    observaciones = ?,
                    fecha_cierre = ?,
                    estado = 'cerrada'
                WHERE id = ?
            ''', (monto_final, ventas_efectivo, ventas_tarjeta, 
                  reparaciones_efectivo, reparaciones_tarjeta,
                  otros_ingresos, otros_egresos, observaciones, fecha_actual, caja_id))
            conn.commit()
            return True, "Caja cerrada exitosamente"
        except Exception as e:
            return False, f"Error al cerrar caja: {str(e)}"
    
    def obtener_caja_abierta(self):
        """Obtener la caja actualmente abierta"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.nombre_completo as usuario
            FROM cajas c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.estado = 'abierta'
            ORDER BY c.id DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def obtener_cajas(self, fecha_desde=None, fecha_hasta=None, limit=50):
        """Obtener historial de cajas"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT c.*, u.nombre_completo as usuario
            FROM cajas c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if fecha_desde:
            query += ' AND DATE(c.fecha_apertura) >= ?'
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += ' AND DATE(c.fecha_apertura) <= ?'
            params.append(fecha_hasta)
        
        query += ' ORDER BY c.id DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def obtener_caja_por_id(self, caja_id):
        """Obtener detalles de una caja específica"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.*, u.nombre_completo as usuario
            FROM cajas c
            JOIN usuarios u ON c.usuario_id = u.id
            WHERE c.id = ?
        ''', (caja_id,))
        
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def eliminar_caja(self, caja_id):
        """Eliminar una caja (solo admin)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar que la caja no esté abierta
            cursor.execute('SELECT estado FROM cajas WHERE id = ?', (caja_id,))
            caja = cursor.fetchone()
            
            if not caja:
                return False, "La caja no existe"
            
            if caja['estado'] == 'abierta':
                return False, "No se puede eliminar una caja abierta. Debe cerrarla primero."
            
            cursor.execute('DELETE FROM cajas WHERE id = ?', (caja_id,))
            conn.commit()
            return True, "Caja eliminada exitosamente"
        except Exception as e:
            return False, f"Error al eliminar caja: {str(e)}"

from datetime import datetime
import unicodedata

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
        
        # Crear tabla de movimientos de caja
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos_caja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caja_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('efectivo', 'transferencia', 'tarjeta')),
                monto REAL NOT NULL,
                categoria TEXT,
                descripcion TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (caja_id) REFERENCES cajas (id)
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
    
    def agregar_movimiento(self, caja_id, tipo, monto, descripcion='', categoria=''):
        """Agregar un movimiento a la caja abierta"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO movimientos_caja (caja_id, tipo, monto, categoria, descripcion)
                VALUES (?, ?, ?, ?, ?)
            ''', (caja_id, tipo, monto, categoria, descripcion))
            conn.commit()
            return True, "Movimiento agregado"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def obtener_movimientos(self, caja_id):
        """Obtener movimientos de una caja"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, tipo, monto, categoria, descripcion, fecha
            FROM movimientos_caja
            WHERE caja_id = ?
            ORDER BY fecha ASC
        ''', (caja_id,))
        
        return [dict(row) for row in cursor.fetchall()]

    def _normalizar_texto(self, texto):
        if not texto:
            return ''
        texto = unicodedata.normalize('NFKD', str(texto))
        texto = texto.encode('ascii', 'ignore').decode('ascii')
        return texto.lower().strip()

    def _clasificar_egreso(self, descripcion):
        texto = self._normalizar_texto(descripcion)
        if any(palabra in texto for palabra in ('tecnico', 'servicio tecnico', 'reparacion tecnica', 'mecanico')):
            return 'Pago técnico'
        if any(palabra in texto for palabra in ('publicidad', 'anuncio', 'ads', 'facebook', 'instagram', 'meta', 'marketing')):
            return 'Publicidad'
        if any(palabra in texto for palabra in ('impuesto', 'iva', 'afip', 'tribut', 'tasas', 'monotributo')):
            return 'Impuestos'
        if any(palabra in texto for palabra in ('empleado', 'sueldo', 'salario', 'nomina', 'nomina', 'liquidacion')):
            return 'Empleados'
        return 'Otros'

    def obtener_resumen_financiero_mes(self, fecha_inicio, fecha_fin):
        """Obtener resumen financiero mensual con ingresos, egresos y ganancia."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        resumen = {
            'ingresos_ventas': 0.0,
            'ingresos_reparaciones': 0.0,
            'ingresos_celulares': 0.0,
            'ingresos_otros_caja': 0.0,
            'ingresos_movimientos': 0.0,
            'egresos_otros_caja': 0.0,
            'egresos_movimientos': 0.0,
            'egresos_por_categoria': {
                'Pago técnico': 0.0,
                'Publicidad': 0.0,
                'Impuestos': 0.0,
                'Empleados': 0.0,
                'Otros': 0.0,
            },
            'ingresos_por_origen': {
                'Reparación': 0.0,
                'Ventas en general': 0.0,
                'Venta celulares': 0.0,
                'Otros': 0.0,
            },
        }

        try:
            cursor.execute('''
                SELECT COALESCE(SUM(total), 0)
                FROM ventas
                WHERE DATE(fecha_venta) >= ? AND DATE(fecha_venta) <= ?
            ''', (fecha_inicio, fecha_fin))
            resumen['ingresos_ventas'] = float(cursor.fetchone()[0] or 0)
        except Exception:
            resumen['ingresos_ventas'] = 0.0

        try:
            cursor.execute('''
                SELECT COALESCE(SUM(COALESCE(sena, 0) + COALESCE(monto_pago_final, 0)), 0)
                FROM reparaciones
                WHERE DATE(fecha_creacion) >= ? AND DATE(fecha_creacion) <= ?
                  AND (COALESCE(sena, 0) > 0 OR estado = 'retirado' OR COALESCE(monto_pago_final, 0) > 0)
            ''', (fecha_inicio, fecha_fin))
            resumen['ingresos_reparaciones'] = float(cursor.fetchone()[0] or 0)
        except Exception:
            resumen['ingresos_reparaciones'] = 0.0

        try:
            cursor.execute('''
                SELECT COALESCE(SUM(COALESCE(sena, 0) + COALESCE(monto_pago_final, 0)), 0)
                FROM ventas_celulares
                WHERE DATE(fecha_venta) >= ? AND DATE(fecha_venta) <= ?
            ''', (fecha_inicio, fecha_fin))
            resumen['ingresos_celulares'] = float(cursor.fetchone()[0] or 0)
        except Exception:
            resumen['ingresos_celulares'] = 0.0

        try:
            cursor.execute('''
                SELECT COALESCE(SUM(otros_ingresos), 0), COALESCE(SUM(otros_egresos), 0)
                FROM cajas
                WHERE fecha_cierre IS NOT NULL
                  AND DATE(fecha_cierre) >= ? AND DATE(fecha_cierre) <= ?
            ''', (fecha_inicio, fecha_fin))
            fila_cajas = cursor.fetchone() or (0, 0)
            resumen['ingresos_otros_caja'] = float(fila_cajas[0] or 0)
            resumen['egresos_otros_caja'] = float(fila_cajas[1] or 0)
        except Exception:
            resumen['ingresos_otros_caja'] = 0.0
            resumen['egresos_otros_caja'] = 0.0

        try:
            cursor.execute('''
                SELECT monto, categoria, descripcion
                FROM movimientos_caja
                WHERE DATE(fecha) >= ? AND DATE(fecha) <= ?
            ''', (fecha_inicio, fecha_fin))
            movimientos = cursor.fetchall()
            for movimiento in movimientos:
                monto = float(movimiento['monto'] or 0)
                categoria = (movimiento['categoria'] or '').strip()
                descripcion = movimiento['descripcion'] or ''
                if monto >= 0:
                    resumen['ingresos_movimientos'] += monto
                    if categoria in resumen['ingresos_por_origen']:
                        resumen['ingresos_por_origen'][categoria] += monto
                    elif categoria:
                        resumen['ingresos_por_origen']['Otros'] += monto
                    else:
                        resumen['ingresos_por_origen']['Otros'] += monto
                else:
                    egreso = abs(monto)
                    resumen['egresos_movimientos'] += egreso
                    if categoria in resumen['egresos_por_categoria']:
                        categoria_egreso = categoria
                    else:
                        categoria_egreso = self._clasificar_egreso(descripcion)
                    resumen['egresos_por_categoria'][categoria_egreso] += egreso
        except Exception:
            pass

        resumen['ingresos_totales'] = (
            resumen['ingresos_ventas']
            + resumen['ingresos_reparaciones']
            + resumen['ingresos_celulares']
            + resumen['ingresos_otros_caja']
            + resumen['ingresos_movimientos']
        )
        resumen['egresos_totales'] = resumen['egresos_otros_caja'] + resumen['egresos_movimientos']
        resumen['ganancia_neta'] = resumen['ingresos_totales'] - resumen['egresos_totales']

        if resumen['egresos_otros_caja']:
            resumen['egresos_por_categoria']['Otros'] += resumen['egresos_otros_caja']

        return resumen
    
    def eliminar_movimiento(self, movimiento_id):
        """Eliminar un movimiento"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM movimientos_caja WHERE id = ?', (movimiento_id,))
            conn.commit()
            return True, "Movimiento eliminado"
        except Exception as e:
            return False, f"Error: {str(e)}"

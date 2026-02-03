from datetime import datetime
import sqlite3
import os
import shutil
from pathlib import Path

class Reparacion:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def generar_numero_orden(self):
        """Generar número de orden único"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        fecha = datetime.now().strftime("%Y%m%d")
        cursor.execute("SELECT COUNT(*) FROM reparaciones WHERE numero_orden LIKE ?", (f'REP-{fecha}-%',))
        count = cursor.fetchone()[0] + 1
        
        return f"REP-{fecha}-{count:04d}"
    
    def agregar_reparacion(self, usuario_id, cliente_nombre, cliente_telefono, cliente_email, 
                          dispositivo, modelo, numero_serie, problema, sena, total,
                          sin_bateria=False, rajado=False, mojado=False, contrasena='', patron='',
                          estado='pendiente', observaciones=''):
        """Agregar nueva reparación"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        numero_orden = self.generar_numero_orden()
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            cursor.execute('''
                INSERT INTO reparaciones (
                    numero_orden, usuario_id, cliente_nombre, cliente_telefono, cliente_email,
                    dispositivo, modelo, numero_serie, problema, sin_bateria, rajado, mojado,
                    contrasena, patron, sena, total, estado, observaciones, fecha_creacion
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (numero_orden, usuario_id, cliente_nombre, cliente_telefono, cliente_email,
                  dispositivo, modelo, numero_serie, problema, 1 if sin_bateria else 0, 
                  1 if rajado else 0, 1 if mojado else 0, contrasena, patron, sena, total, 
                  estado, observaciones, fecha_actual))
            
            conn.commit()
            return True, numero_orden
        except Exception as e:
            return False, str(e)
    
    def obtener_reparaciones(self, filtro_estado=None):
        """Obtener lista de reparaciones"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        if filtro_estado:
            cursor.execute('''
                SELECT * FROM reparaciones 
                WHERE estado = ?
                ORDER BY fecha_creacion DESC
            ''', (filtro_estado,))
        else:
            cursor.execute('''
                SELECT * FROM reparaciones 
                ORDER BY fecha_creacion DESC
            ''')
        
        # Convertir sqlite3.Row a diccionarios
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def obtener_reparacion(self, reparacion_id):
        """Obtener detalles de una reparación"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM reparaciones WHERE id = ?', (reparacion_id,))
        result = cursor.fetchone()
        
        if result:
            return dict(result)
        return None
    
    def actualizar_reparacion(self, reparacion_id, cliente_nombre=None, cliente_telefono=None, 
                             cliente_email=None, dispositivo=None, modelo=None, numero_serie=None,
                             problema=None, sena=None, total=None, sin_bateria=None, rajado=None,
                             mojado=None, contrasena=None, patron=None, estado=None, 
                             observaciones=None):
        """Actualizar reparación"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        # Obtener reparación actual
        reparacion = self.obtener_reparacion(reparacion_id)
        if not reparacion:
            return False, "Reparación no encontrada"
        
        # Actualizar solo los campos proporcionados
        updates = []
        values = []
        
        if cliente_nombre is not None:
            updates.append("cliente_nombre = ?")
            values.append(cliente_nombre)
        if cliente_telefono is not None:
            updates.append("cliente_telefono = ?")
            values.append(cliente_telefono)
        if cliente_email is not None:
            updates.append("cliente_email = ?")
            values.append(cliente_email)
        if dispositivo is not None:
            updates.append("dispositivo = ?")
            values.append(dispositivo)
        if modelo is not None:
            updates.append("modelo = ?")
            values.append(modelo)
        if numero_serie is not None:
            updates.append("numero_serie = ?")
            values.append(numero_serie)
        if problema is not None:
            updates.append("problema = ?")
            values.append(problema)
        if sena is not None:
            updates.append("sena = ?")
            values.append(sena)
        if total is not None:
            updates.append("total = ?")
            values.append(total)
        if sin_bateria is not None:
            updates.append("sin_bateria = ?")
            values.append(1 if sin_bateria else 0)
        if rajado is not None:
            updates.append("rajado = ?")
            values.append(1 if rajado else 0)
        if mojado is not None:
            updates.append("mojado = ?")
            values.append(1 if mojado else 0)
        if contrasena is not None:
            updates.append("contrasena = ?")
            values.append(contrasena)
        if patron is not None:
            updates.append("patron = ?")
            values.append(patron)
        if estado is not None:
            updates.append("estado = ?")
            values.append(estado)
            if estado == 'completada':
                fecha_entrega = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updates.append("fecha_entrega = ?")
                values.append(fecha_entrega)
        if observaciones is not None:
            updates.append("observaciones = ?")
            values.append(observaciones)
        
        if not updates:
            return False, "No hay campos para actualizar"
        
        values.append(reparacion_id)
        
        try:
            query = f"UPDATE reparaciones SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            return True, "Reparación actualizada correctamente"
        except Exception as e:
            return False, str(e)
    
    def eliminar_reparacion(self, reparacion_id):
        """Eliminar reparación"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM reparaciones WHERE id = ?', (reparacion_id,))
            conn.commit()
            return True, "Reparación eliminada correctamente"
        except Exception as e:
            return False, str(e)
    
    def obtener_estadisticas(self):
        """Obtener estadísticas de reparaciones"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de reparaciones
        cursor.execute("SELECT COUNT(*) FROM reparaciones")
        stats['total'] = cursor.fetchone()[0]
        
        # Por estado
        for estado in ['pendiente', 'en_proceso', 'completada', 'cancelada']:
            cursor.execute("SELECT COUNT(*) FROM reparaciones WHERE estado = ?", (estado,))
            stats[estado] = cursor.fetchone()[0]
        
        # Total de reparaciones completadas
        cursor.execute("SELECT SUM(total) FROM reparaciones WHERE estado = 'completada'")
        stats['total_completadas'] = cursor.fetchone()[0] or 0
        
        # Total cobrado (seña + total de completadas)
        cursor.execute("SELECT SUM(sena) FROM reparaciones")
        stats['total_senado'] = cursor.fetchone()[0] or 0
        
        return stats
    
    def _carpeta_reparacion(self, reparacion):
        """Devuelve la carpeta específica de la reparación dentro de fotos_reparaciones"""
        numero = reparacion.get('numero_orden', f"rep_{reparacion.get('id','')}")
        carpeta = os.path.join(self.db_manager.fotos_path, f"ticket_{numero}")
        os.makedirs(carpeta, exist_ok=True)
        return carpeta

    def agregar_foto(self, reparacion_id, foto_path):
        """Agregar foto a una reparación. Retorna la ruta de la foto guardada."""
        try:
            # Obtener reparación
            reparacion = self.obtener_reparacion(reparacion_id)
            if not reparacion:
                return False, "Reparación no encontrada"
            
            # Carpeta específica del ticket
            carpeta_ticket = self._carpeta_reparacion(reparacion)
            
            # Determinar próximo número de foto dentro de la carpeta
            existentes = [f for f in os.listdir(carpeta_ticket) if f.lower().endswith('.jpg')]
            contador = len(existentes) + 1
            nombre_foto = f"foto_{contador:02d}.jpg"
            ruta_destino = os.path.join(carpeta_ticket, nombre_foto)
            
            # Copiar foto
            shutil.copy(foto_path, ruta_destino)
            
            return True, ruta_destino
        except Exception as e:
            return False, str(e)
    
    def obtener_fotos(self, reparacion_id):
        """Obtener lista de fotos de una reparación"""
        try:
            reparacion = self.obtener_reparacion(reparacion_id)
            if not reparacion:
                return []
            carpeta_ticket = self._carpeta_reparacion(reparacion)
            if not os.path.exists(carpeta_ticket):
                return []
            archivos = [os.path.join(carpeta_ticket, f) for f in os.listdir(carpeta_ticket) 
                       if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
            archivos.sort()
            # Validar que los archivos existan
            archivos = [f for f in archivos if os.path.exists(f) and os.path.isfile(f)]
            return archivos
        except Exception:
            return []
    
    def eliminar_foto(self, reparacion_id, numero_foto):
        """Eliminar una foto específica de una reparación"""
        try:
            reparacion = self.obtener_reparacion(reparacion_id)
            if not reparacion:
                return False, "Reparación no encontrada"
            carpeta_ticket = self._carpeta_reparacion(reparacion)
            nombre_foto = f"foto_{numero_foto:02d}.jpg"
            ruta_foto = os.path.join(carpeta_ticket, nombre_foto)
            
            if os.path.exists(ruta_foto):
                os.remove(ruta_foto)
                # Renumerar fotos después de la eliminada
                self._renumerar_fotos(reparacion, numero_foto)
                return True, "Foto eliminada correctamente"
            return False, "Foto no encontrada"
        except Exception as e:
            return False, str(e)
    
    def _renumerar_fotos(self, reparacion, desde_numero):
        """Renumerar fotos después de eliminar una"""
        try:
            carpeta_ticket = self._carpeta_reparacion(reparacion)
            contador = desde_numero + 1
            while True:
                nombre_actual = f"foto_{contador:02d}.jpg"
                ruta_actual = os.path.join(carpeta_ticket, nombre_actual)
                if not os.path.exists(ruta_actual):
                    break
                nombre_nuevo = f"foto_{contador - 1:02d}.jpg"
                ruta_nueva = os.path.join(carpeta_ticket, nombre_nuevo)
                os.rename(ruta_actual, ruta_nueva)
                contador += 1
        except Exception:
            pass
    
    def eliminar_todas_fotos(self, reparacion_id):
        """Eliminar todas las fotos de una reparación"""
        try:
            reparacion = self.obtener_reparacion(reparacion_id)
            if not reparacion:
                return False, "Reparación no encontrada"
            carpeta_ticket = self._carpeta_reparacion(reparacion)
            if os.path.exists(carpeta_ticket):
                for foto in os.listdir(carpeta_ticket):
                    ruta = os.path.join(carpeta_ticket, foto)
                    if os.path.isfile(ruta):
                        os.remove(ruta)
            return True, "Fotos eliminadas correctamente"
        except Exception as e:
            return False, str(e)

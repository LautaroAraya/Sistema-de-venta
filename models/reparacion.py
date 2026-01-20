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
        
        try:
            cursor.execute('''
                INSERT INTO reparaciones (
                    numero_orden, usuario_id, cliente_nombre, cliente_telefono, cliente_email,
                    dispositivo, modelo, numero_serie, problema, sin_bateria, rajado, mojado,
                    contrasena, patron, sena, total, estado, observaciones
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (numero_orden, usuario_id, cliente_nombre, cliente_telefono, cliente_email,
                  dispositivo, modelo, numero_serie, problema, 1 if sin_bateria else 0, 
                  1 if rajado else 0, 1 if mojado else 0, contrasena, patron, sena, total, 
                  estado, observaciones))
            
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
                updates.append("fecha_entrega = CURRENT_TIMESTAMP")
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
    
    def agregar_foto(self, reparacion_id, foto_path):
        """Agregar foto a una reparación. Retorna la ruta de la foto guardada."""
        try:
            # Obtener reparación
            reparacion = self.obtener_reparacion(reparacion_id)
            if not reparacion:
                return False, "Reparación no encontrada"
            
            # Obtener carpeta de fotos
            fotos_dir = self.db_manager.fotos_path
            
            # Contar fotos existentes para esta reparación
            contador = 1
            while True:
                nombre_foto = f"rep_{reparacion_id:05d}_{contador}.jpg"
                ruta_destino = os.path.join(fotos_dir, nombre_foto)
                if not os.path.exists(ruta_destino):
                    break
                contador += 1
            
            # Copiar foto
            shutil.copy(foto_path, ruta_destino)
            
            return True, ruta_destino
        except Exception as e:
            return False, str(e)
    
    def obtener_fotos(self, reparacion_id):
        """Obtener lista de fotos de una reparación"""
        try:
            fotos_dir = self.db_manager.fotos_path
            fotos = []
            
            for i in range(1, 100):  # Máximo 99 fotos por reparación
                nombre_foto = f"rep_{reparacion_id:05d}_{i}.jpg"
                ruta_foto = os.path.join(fotos_dir, nombre_foto)
                if os.path.exists(ruta_foto):
                    fotos.append(ruta_foto)
                else:
                    break
            
            return fotos
        except Exception as e:
            return []
    
    def eliminar_foto(self, reparacion_id, numero_foto):
        """Eliminar una foto específica de una reparación"""
        try:
            fotos_dir = self.db_manager.fotos_path
            nombre_foto = f"rep_{reparacion_id:05d}_{numero_foto}.jpg"
            ruta_foto = os.path.join(fotos_dir, nombre_foto)
            
            if os.path.exists(ruta_foto):
                os.remove(ruta_foto)
                # Renumerar fotos después de la eliminada
                self._renumerar_fotos(reparacion_id, numero_foto)
                return True, "Foto eliminada correctamente"
            return False, "Foto no encontrada"
        except Exception as e:
            return False, str(e)
    
    def _renumerar_fotos(self, reparacion_id, desde_numero):
        """Renumerar fotos después de eliminar una"""
        try:
            fotos_dir = self.db_manager.fotos_path
            
            # Buscar fotos después de la eliminada y renumerarlas
            contador = desde_numero + 1
            while True:
                nombre_actual = f"rep_{reparacion_id:05d}_{contador}.jpg"
                ruta_actual = os.path.join(fotos_dir, nombre_actual)
                
                if not os.path.exists(ruta_actual):
                    break
                
                nombre_nuevo = f"rep_{reparacion_id:05d}_{contador - 1}.jpg"
                ruta_nueva = os.path.join(fotos_dir, nombre_nuevo)
                os.rename(ruta_actual, ruta_nueva)
                
                contador += 1
        except Exception as e:
            pass
    
    def eliminar_todas_fotos(self, reparacion_id):
        """Eliminar todas las fotos de una reparación"""
        try:
            fotos = self.obtener_fotos(reparacion_id)
            for foto in fotos:
                if os.path.exists(foto):
                    os.remove(foto)
            return True, "Fotos eliminadas correctamente"
        except Exception as e:
            return False, str(e)

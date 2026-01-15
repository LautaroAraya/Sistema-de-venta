from datetime import datetime

class Configuracion:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def obtener_configuracion(self):
        """Obtener la configuración del sistema"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM configuracion WHERE id = 1")
        result = cursor.fetchone()
        
        if result:
            return dict(result)
        return {'nombre_sistema': 'SISTEMA DE VENTAS', 'logo_path': None}
    
    def actualizar_nombre_sistema(self, nombre):
        """Actualizar el nombre del sistema"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE configuracion 
            SET nombre_sistema = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (nombre,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def actualizar_logo(self, logo_path):
        """Actualizar la ruta del logo"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE configuracion 
            SET logo_path = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (logo_path,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def actualizar_configuracion(self, nombre, logo_path):
        """Actualizar nombre y logo del sistema"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE configuracion 
            SET nombre_sistema = ?, logo_path = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE id = 1
        ''', (nombre, logo_path))
        
        conn.commit()
        return cursor.rowcount > 0

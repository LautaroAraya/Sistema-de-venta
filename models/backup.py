import shutil
import os
from datetime import datetime
import sqlite3

class Backup:
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def crear_backup(self, ruta_destino):
        """Crear copia de seguridad completa: base de datos y carpetas de fotos en un ZIP"""
        import zipfile
        try:
            db_path = self.db_manager.db_path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"backup_sistema_ventas_{timestamp}.zip"
            if not ruta_destino:
                ruta_destino = os.path.expanduser("~/Desktop")
            ruta_completa = os.path.join(ruta_destino, nombre_archivo)

            # Cerrar conexión actual para asegurar integridad
            self.db_manager.close()

            with zipfile.ZipFile(ruta_completa, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                # Agregar base de datos
                backup_zip.write(db_path, arcname=os.path.join('database', os.path.basename(db_path)))

                # Agregar carpetas de fotos
                carpetas = ['fotos_reparaciones', 'fotos_temporales']
                base_dir = os.path.dirname(os.path.dirname(db_path))
                for carpeta in carpetas:
                    carpeta_path = os.path.join(base_dir, carpeta)
                    if os.path.exists(carpeta_path):
                        for root, dirs, files in os.walk(carpeta_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, base_dir)
                                backup_zip.write(file_path, arcname=arcname)

            # Reconectar
            self.db_manager.get_connection()
            return True, ruta_completa
        except Exception as e:
            return False, str(e)
    
    def restaurar_backup(self, ruta_backup):
        """Restaurar base de datos desde un backup"""
        try:
            # Validar que el archivo existe
            if not os.path.exists(ruta_backup):
                return False, "El archivo de backup no existe"
            
            # Validar que es una BD válida
            try:
                test_conn = sqlite3.connect(ruta_backup)
                test_conn.execute("SELECT 1")
                test_conn.close()
            except:
                return False, "El archivo no es una base de datos válida"
            
            # Obtener ruta de la BD actual
            db_path = self.db_manager.db_path
            
            # Crear backup de la BD actual antes de restaurar
            backup_actual = db_path + ".backup"
            shutil.copy2(db_path, backup_actual)
            
            # Cerrar conexión
            self.db_manager.close()
            
            try:
                # Copiar el backup a la BD actual
                shutil.copy2(ruta_backup, db_path)
                
                # Reconectar
                self.db_manager.get_connection()
                # Asegurar estructura actualizada en backups antiguos
                self.db_manager.init_database()
                
                return True, "Base de datos restaurada correctamente"
            except Exception as e:
                # Si falla, restaurar el backup anterior
                shutil.copy2(backup_actual, db_path)
                self.db_manager.get_connection()
                return False, f"Error al restaurar: {str(e)}"
            finally:
                # Limpiar backup temporal
                if os.path.exists(backup_actual):
                    os.remove(backup_actual)
        
        except Exception as e:
            return False, str(e)
    
    def obtener_info_backup(self, ruta_backup):
        """Obtener información de un backup"""
        try:
            if not os.path.exists(ruta_backup):
                return None
            
            # Información del archivo
            size_bytes = os.path.getsize(ruta_backup)
            size_mb = size_bytes / (1024 * 1024)
            
            # Fecha de modificación
            timestamp = os.path.getmtime(ruta_backup)
            fecha = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
            
            # Contar registros
            try:
                conn = sqlite3.connect(ruta_backup)
                cursor = conn.cursor()
                
                tablas = {
                    'usuarios': 0,
                    'productos': 0,
                    'proveedores': 0,
                    'categorias': 0,
                    'ventas': 0,
                    'detalles_venta': 0,
                    'caja': 0,
                    'reparaciones': 0
                }
                
                for tabla in tablas:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                        tablas[tabla] = cursor.fetchone()[0]
                    except:
                        # Si la tabla no existe, dejar en 0
                        tablas[tabla] = 0
                
                conn.close()
                
                return {
                    'nombre': os.path.basename(ruta_backup),
                    'tamaño': f"{size_mb:.2f} MB",
                    'fecha': fecha,
                    'usuarios': tablas['usuarios'],
                    'productos': tablas['productos'],
                    'proveedores': tablas['proveedores'],
                    'categorias': tablas['categorias'],
                    'ventas': tablas['ventas'],
                    'detalles_venta': tablas['detalles_venta'],
                    'caja': tablas['caja'],
                    'reparaciones': tablas['reparaciones']
                }
            except:
                return {
                    'nombre': os.path.basename(ruta_backup),
                    'tamaño': f"{size_mb:.2f} MB",
                    'fecha': fecha,
                    'usuarios': '?',
                    'productos': '?',
                    'proveedores': '?',
                    'categorias': '?',
                    'ventas': '?',
                    'detalles_venta': '?',
                    'caja': '?',
                    'reparaciones': '?'
                }
        except:
            return None

"""
Sistema de registro de errores para el Sistema de Ventas
Registra todos los errores en archivos .txt para revisión del administrador
"""

import os
import sys
import traceback
from datetime import datetime
import json

class ErrorLogger:
    def __init__(self, base_path=None):
        """
        Inicializar el logger de errores
        
        Args:
            base_path: Ruta base del proyecto (opcional, se auto-detecta)
        """
        if base_path is None:
            base_path = self._find_project_root()
        
        self.base_path = base_path
        
        # Usar AppData si estamos en Program Files (sin permisos de escritura)
        if self._is_protected_path(base_path):
            appdata = os.path.join(os.environ.get('LOCALAPPDATA', os.path.expanduser('~')), 'SistemaVentas')
            self.errors_dir = os.path.join(appdata, "logs", "errors")
        else:
            self.errors_dir = os.path.join(base_path, "logs", "errors")
        
        self.error_log_file = os.path.join(self.errors_dir, "error_log.txt")
        self.error_summary_file = os.path.join(self.errors_dir, "errores_resumen.json")
        
        # Crear directorio de logs si no existe
        try:
            os.makedirs(self.errors_dir, exist_ok=True)
        except PermissionError:
            # Si falla, usar temp
            import tempfile
            self.errors_dir = os.path.join(tempfile.gettempdir(), 'SistemaVentas', 'logs', 'errors')
            os.makedirs(self.errors_dir, exist_ok=True)
            self.error_log_file = os.path.join(self.errors_dir, "error_log.txt")
            self.error_summary_file = os.path.join(self.errors_dir, "errores_resumen.json")
        
        # Crear archivo de log si no existe
        try:
            if not os.path.exists(self.error_log_file):
                with open(self.error_log_file, 'w', encoding='utf-8') as f:
                    f.write("=== REGISTRO DE ERRORES - SISTEMA DE VENTAS ===\n")
                    f.write(f"Creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
        except Exception:
            pass  # Si no puede crear el archivo, continuar sin logs
    
    def _is_protected_path(self, path):
        """Verificar si la ruta está en un directorio protegido del sistema"""
        protected_paths = ['Program Files', 'Program Files (x86)', 'Windows']
        path_upper = path.upper()
        return any(protected in path_upper for protected in protected_paths)
    
    def _find_project_root(self):
        """Encontrar la carpeta raíz del proyecto"""
        if getattr(sys, 'frozen', False):
            # Si es ejecutable
            start_path = os.path.dirname(sys.executable)
        else:
            # Si es script
            start_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Buscar version.txt en el directorio actual o padres
        current = start_path
        for _ in range(10):
            if os.path.exists(os.path.join(current, "version.txt")):
                return current
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        
        return start_path
    
    def log_error(self, error_type, error_message, error_traceback=None, 
                  context=None, severity="ERROR"):
        """
        Registrar un error en el archivo de log
        
        Args:
            error_type: Tipo de error (ej: "ValueError", "DatabaseError")
            error_message: Mensaje descriptivo del error
            error_traceback: Traceback completo del error (opcional)
            context: Contexto adicional (ej: usuario, módulo, acción) (opcional)
            severity: Nivel de severidad (ERROR, WARNING, CRITICAL)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Crear entrada de error
        error_entry = f"\n{'=' * 80}\n"
        error_entry += f"[{severity}] {timestamp}\n"
        error_entry += f"Tipo: {error_type}\n"
        error_entry += f"Mensaje: {error_message}\n"
        
        if context:
            error_entry += f"\nContexto:\n"
            for key, value in context.items():
                error_entry += f"  - {key}: {value}\n"
        
        if error_traceback:
            error_entry += f"\nTraceback:\n{error_traceback}\n"
        
        error_entry += "=" * 80 + "\n"
        
        # Escribir en archivo
        try:
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(error_entry)
            
            # Actualizar resumen de errores
            self._update_error_summary(error_type, severity, timestamp)
            
            return True
        except Exception as e:
            print(f"Error al escribir en el log: {e}")
            return False
    
    def log_exception(self, exception, context=None):
        """
        Registrar una excepción de Python
        
        Args:
            exception: Objeto de excepción
            context: Contexto adicional (opcional)
        """
        error_type = type(exception).__name__
        error_message = str(exception)
        error_traceback = ''.join(traceback.format_exception(
            type(exception), exception, exception.__traceback__
        ))
        
        return self.log_error(
            error_type=error_type,
            error_message=error_message,
            error_traceback=error_traceback,
            context=context,
            severity="ERROR"
        )
    
    def _update_error_summary(self, error_type, severity, timestamp):
        """Actualizar resumen de errores en JSON"""
        try:
            # Leer resumen existente
            if os.path.exists(self.error_summary_file):
                with open(self.error_summary_file, 'r', encoding='utf-8') as f:
                    summary = json.load(f)
            else:
                summary = {
                    "total_errores": 0,
                    "ultimo_error": None,
                    "errores_por_tipo": {},
                    "errores_por_severidad": {
                        "ERROR": 0,
                        "WARNING": 0,
                        "CRITICAL": 0
                    }
                }
            
            # Actualizar contadores
            summary["total_errores"] += 1
            summary["ultimo_error"] = timestamp
            
            if error_type not in summary["errores_por_tipo"]:
                summary["errores_por_tipo"][error_type] = 0
            summary["errores_por_tipo"][error_type] += 1
            
            summary["errores_por_severidad"][severity] += 1
            
            # Guardar resumen
            with open(self.error_summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=4, ensure_ascii=False)
        
        except Exception as e:
            print(f"Error al actualizar resumen: {e}")
    
    def get_error_summary(self):
        """Obtener resumen de errores"""
        try:
            if os.path.exists(self.error_summary_file):
                with open(self.error_summary_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except:
            return None
    
    def get_recent_errors(self, limit=50):
        """
        Obtener los errores más recientes
        
        Args:
            limit: Número máximo de errores a retornar
        
        Returns:
            Lista de strings con las entradas de error
        """
        try:
            if not os.path.exists(self.error_log_file):
                return []
            
            with open(self.error_log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Dividir por separadores
            errors = content.split('=' * 80)
            
            # Filtrar entradas vacías y tomar las últimas
            errors = [e.strip() for e in errors if e.strip() and not e.strip().startswith('REGISTRO DE ERRORES')]
            
            return errors[-limit:] if len(errors) > limit else errors
        
        except Exception as e:
            print(f"Error al leer errores: {e}")
            return []
    
    def clear_old_errors(self, days=30):
        """
        Limpiar errores antiguos (crear backup)
        
        Args:
            days: Días de antigüedad para considerar errores viejos
        """
        try:
            if not os.path.exists(self.error_log_file):
                return
            
            # Crear backup
            backup_name = f"error_log_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            backup_path = os.path.join(self.errors_dir, backup_name)
            
            import shutil
            shutil.copy2(self.error_log_file, backup_path)
            
            # Resetear archivo principal
            with open(self.error_log_file, 'w', encoding='utf-8') as f:
                f.write("=== REGISTRO DE ERRORES - SISTEMA DE VENTAS ===\n")
                f.write(f"Limpiado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Backup guardado en: {backup_name}\n")
                f.write("=" * 60 + "\n\n")
            
            # Resetear resumen
            if os.path.exists(self.error_summary_file):
                os.remove(self.error_summary_file)
            
            return True
        except Exception as e:
            print(f"Error al limpiar logs: {e}")
            return False
    
    def get_log_file_path(self):
        """Obtener ruta del archivo de log"""
        return self.error_log_file


# Instancia global del logger
_global_logger = None

def get_error_logger(base_path=None):
    """Obtener instancia global del logger de errores"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ErrorLogger(base_path)
    return _global_logger


def log_error(error_type, error_message, error_traceback=None, context=None, severity="ERROR"):
    """Función de conveniencia para registrar errores"""
    logger = get_error_logger()
    return logger.log_error(error_type, error_message, error_traceback, context, severity)


def log_exception(exception, context=None):
    """Función de conveniencia para registrar excepciones"""
    logger = get_error_logger()
    return logger.log_exception(exception, context)

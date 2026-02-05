from utils.updater import UpdateManager
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# ====== VALIDACIÓN DE LICENCIA (DEBE SER LO PRIMERO) ======
from utils.validador_public import validar_licencia_inicio

resultado_licencia = validar_licencia_inicio()
if resultado_licencia is None:
    sys.exit(1)
# =========================================================

def find_project_root():
    """Encontrar la carpeta raíz del proyecto buscando version.txt
    
    Esto es crítico para que después de actualizaciones, siempre se use
    la carpeta correcta (Sistema de venta) sin importar dónde se ejecute.
    """
    if getattr(sys, 'frozen', False):
        # Si es EXE, buscar version.txt en el directorio del ejecutable y padres
        start_path = os.path.dirname(sys.executable)
    else:
        # Si es script, buscar a partir del directorio de main.py
        start_path = os.path.dirname(os.path.abspath(__file__))
    
    # Si estamos en una carpeta "dist", buscar en la carpeta padre
    if os.path.basename(os.path.abspath(start_path)).lower() == 'dist':
        parent = os.path.dirname(start_path)
        if os.path.exists(os.path.join(parent, "version.txt")):
            return parent
    
    # Primero verificar si existe version.txt en start_path
    if os.path.exists(os.path.join(start_path, "version.txt")):
        return start_path
    
    # Si no, buscar en directorios padre
    current = start_path
    for _ in range(15):  # Limitar a 15 niveles de profundidad
        parent = os.path.dirname(current)
        if parent == current:  # Llegamos a la raíz del filesystem
            break
        version_file = os.path.join(parent, "version.txt")
        if os.path.exists(version_file):
            return parent
        current = parent
    
    # Si no se encuentra, usar start_path
    return start_path

# Agregar el directorio raíz al path
BASE_DIR = find_project_root()

# VALIDACIÓN CRÍTICA: Si no hay version.txt, buscar "Sistema de venta" en la ruta
if not os.path.exists(os.path.join(BASE_DIR, "version.txt")):
    parts = BASE_DIR.split(os.sep)
    if "Sistema de venta" in parts:
        idx = parts.index("Sistema de venta")
        sistema_venta_path = os.sep.join(parts[:idx+1])
        if os.path.exists(os.path.join(sistema_venta_path, "version.txt")):
            BASE_DIR = sistema_venta_path

sys.path.insert(0, BASE_DIR)

from database.db_manager import DatabaseManager
from views.login_view import LoginView
from views.main_view import MainView

class SistemaVentas:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Ocultar ventana principal temporalmente
        # Inicializar gestor de actualizaciones
        self.update_manager = UpdateManager(BASE_DIR)
        # self.update_manager.check_updates_async(self.root)  # Deshabilitado: no buscar ni recibir actualizaciones

        # Ejecutar migraciones automáticas de forma segura
        try:
            # Importación dinámica para evitar problemas de ruta inicial
            from migrar_metodo_pago_recargo import ejecutar_migracion
            ejecutar_migracion(BASE_DIR)
        except Exception as e:
            print(f"Aviso: No se pudo realizar la migración automática: {e}")

        # Inicializar base de datos
        self.db_manager = DatabaseManager()

        # Mostrar login
        self.mostrar_login()
        
    def mostrar_login(self):
        """Mostrar ventana de login"""
        login_window = tk.Toplevel(self.root)
        LoginView(login_window, self.db_manager, self.on_login_success)
    
    def on_login_success(self, user_data):
        """Callback cuando el login es exitoso"""
        # Cerrar todas las ventanas toplevel (login)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()
        
        # Mostrar ventana principal
        self.root.deiconify()
        MainView(self.root, self.db_manager, user_data, self.on_logout)

    def on_logout(self):
        """Volver al login al cerrar sesión"""
        # Limpiar todos los widgets de la ventana principal
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Ocultar la ventana principal
        self.root.withdraw()
        
        # Volver a mostrar el login
        self.mostrar_login()
    
    def run(self):
        """Ejecutar aplicación"""
        try:
            self.root.mainloop()
        finally:
            # Cerrar conexión a la base de datos al salir
            self.db_manager.close()

if __name__ == "__main__":
    # Importar logger de errores
    from utils.error_logger import get_error_logger, log_exception
    
    # Inicializar logger
    error_logger = get_error_logger(BASE_DIR)
    
    # Configurar excepciones no capturadas
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Registrar el error en el archivo de log
        import traceback
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        error_logger.log_error(
            error_type=exc_type.__name__,
            error_message=str(exc_value),
            error_traceback=tb_str,
            context={'origen': 'Excepción no capturada'},
            severity='CRITICAL'
        )
        
        error_msg = f"Error no controlado: {exc_value}\n\nEl error ha sido registrado en el sistema."
        messagebox.showerror("Error", error_msg)
    
    sys.excepthook = handle_exception
    
    # Iniciar aplicación
    try:
        app = SistemaVentas()
        app.run()
    except Exception as e:
        log_exception(e, context={'origen': 'Inicialización de aplicación'})
        messagebox.showerror("Error Fatal", 
                           f"No se pudo iniciar la aplicación: {e}\n\nEl error ha sido registrado.")

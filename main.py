import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Agregar el directorio raíz al path
if getattr(sys, 'frozen', False):
    # Si está empaquetado como exe
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Si está en desarrollo
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, BASE_DIR)

from database.db_manager import DatabaseManager
from views.login_view import LoginView
from views.main_view import MainView
from utils.updater import UpdateManager

class SistemaVentas:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Ocultar ventana principal temporalmente
        
        # Inicializar gestor de actualizaciones
        self.update_manager = UpdateManager(BASE_DIR)
        self.update_manager.check_updates_async(self.root)
        
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
    # Configurar excepciones no capturadas
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = f"Error no controlado: {exc_value}"
        messagebox.showerror("Error", error_msg)
    
    sys.excepthook = handle_exception
    
    # Iniciar aplicación
    app = SistemaVentas()
    app.run()

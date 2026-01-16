"""
Vista para visualizar y gestionar errores registrados del sistema
Solo accesible para administradores
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
from datetime import datetime
from utils.error_logger import get_error_logger

class ErroresView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.error_logger = get_error_logger()
        
        # Verificar que el usuario sea administrador
        if user_data['rol'] != 'admin':
            messagebox.showerror("Acceso Denegado", 
                               "Solo los administradores pueden ver el registro de errores")
            return
        
        self.create_widgets()
        self.cargar_errores()
    
    def create_widgets(self):
        """Crear widgets de la interfaz"""
        self.parent.configure(bg='#F0F4F8')
        
        # Título
        title_frame = tk.Frame(self.parent, bg='#EF4444', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="🐛 REGISTRO DE ERRORES DEL SISTEMA",
                font=("Arial", 18, "bold"),
                bg='#EF4444',
                fg='white').pack(expand=True)
        
        # Frame de estadísticas
        stats_frame = tk.Frame(self.parent, bg='white', relief=tk.RIDGE, bd=2)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stats_frame, 
                text="📊 Resumen de Errores", 
                font=("Arial", 12, "bold"), 
                bg='white').grid(row=0, column=0, columnspan=6, sticky=tk.W, padx=10, pady=5)
        
        # Etiquetas de estadísticas
        tk.Label(stats_frame, text="Total de Errores:", bg='white', fg='black').grid(row=1, column=0, sticky=tk.W, padx=10, pady=2)
        self.total_errores_label = tk.Label(stats_frame, text="0", font=("Arial", 10, "bold"), bg='white', fg='#EF4444')
        self.total_errores_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        tk.Label(stats_frame, text="Último Error:", bg='white', fg='black').grid(row=1, column=2, sticky=tk.W, padx=20, pady=2)
        self.ultimo_error_label = tk.Label(stats_frame, text="N/A", font=("Arial", 10), bg='white', fg='black')
        self.ultimo_error_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # Botones de acción
        btn_frame = tk.Frame(self.parent, bg='#F0F4F8')
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame,
                 text="🔄 Actualizar",
                 font=("Arial", 10, "bold"),
                 bg='#3B82F6',
                 fg='white',
                 activebackground='#2563EB',
                 bd=0,
                 padx=15,
                 pady=8,
                 cursor='hand2',
                 command=self.cargar_errores).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame,
                 text="📂 Abrir Archivo de Log",
                 font=("Arial", 10, "bold"),
                 bg='#10B981',
                 fg='white',
                 activebackground='#059669',
                 bd=0,
                 padx=15,
                 pady=8,
                 cursor='hand2',
                 command=self.abrir_archivo_log).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame,
                 text="🗑️ Limpiar Logs Antiguos",
                 font=("Arial", 10, "bold"),
                 bg='#F59E0B',
                 fg='white',
                 activebackground='#D97706',
                 bd=0,
                 padx=15,
                 pady=8,
                 cursor='hand2',
                 command=self.limpiar_logs).pack(side=tk.LEFT, padx=5)
        
        # Frame para lista de errores
        list_frame = tk.LabelFrame(self.parent, text="Errores Registrados", 
                                   font=("Arial", 11, "bold"),
                                   bg='white', fg='black')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox con scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.errores_listbox = tk.Listbox(list_frame,
                                         yscrollcommand=scrollbar.set,
                                         font=("Courier New", 9),
                                         height=10,
                                         bg='#FEF2F2',
                                         selectmode=tk.SINGLE)
        self.errores_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.errores_listbox.yview)
        
        self.errores_listbox.bind('<<ListboxSelect>>', self.on_error_select)
        
        # Frame para detalles del error
        detail_frame = tk.LabelFrame(self.parent, text="Detalles del Error Seleccionado",
                                    font=("Arial", 11, "bold"),
                                    bg='white', fg='black')
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.error_detail_text = scrolledtext.ScrolledText(detail_frame,
                                                          font=("Courier New", 9),
                                                          height=12,
                                                          bg='#FFFBEB',
                                                          wrap=tk.WORD)
        self.error_detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def cargar_errores(self):
        """Cargar errores desde el logger"""
        try:
            # Limpiar listbox
            self.errores_listbox.delete(0, tk.END)
            
            # Obtener resumen de errores
            summary = self.error_logger.get_error_summary()
            if summary:
                self.total_errores_label.config(text=str(summary.get('total_errores', 0)))
                ultimo = summary.get('ultimo_error', 'N/A')
                self.ultimo_error_label.config(text=ultimo if ultimo else 'N/A')
            else:
                self.total_errores_label.config(text="0")
                self.ultimo_error_label.config(text="N/A")
            
            # Obtener errores recientes
            self.errores = self.error_logger.get_recent_errors(limit=100)
            
            if not self.errores:
                self.errores_listbox.insert(tk.END, "No hay errores registrados")
                self.error_detail_text.delete('1.0', tk.END)
                self.error_detail_text.insert('1.0', "No hay errores para mostrar")
                return
            
            # Mostrar resumen en listbox
            for i, error in enumerate(reversed(self.errores), 1):
                # Extraer primera línea que contiene la fecha
                lines = error.split('\n')
                first_line = lines[0] if lines else "Error desconocido"
                
                # Extraer timestamp
                timestamp = "N/A"
                tipo = "Error"
                for line in lines:
                    if line.startswith('[') and ']' in line:
                        timestamp = line.split(']')[1].strip() if ']' in line else line
                    if line.startswith('Tipo:'):
                        tipo = line.replace('Tipo:', '').strip()
                
                display_text = f"{i}. [{timestamp}] {tipo}"
                self.errores_listbox.insert(tk.END, display_text)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar errores: {e}")
            from utils.error_logger import log_exception
            log_exception(e, context={
                'usuario': self.user_data.get('usuario', 'desconocido'),
                'vista': 'ErroresView',
                'accion': 'cargar_errores'
            })
    
    def on_error_select(self, event):
        """Mostrar detalles del error seleccionado"""
        try:
            selection = self.errores_listbox.curselection()
            if not selection:
                return
            
            index = selection[0]
            
            # Los errores están en orden reverso en la lista
            error_index = len(self.errores) - 1 - index
            
            if 0 <= error_index < len(self.errores):
                error_text = self.errores[error_index]
                
                # Mostrar en el área de detalles
                self.error_detail_text.delete('1.0', tk.END)
                self.error_detail_text.insert('1.0', error_text)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {e}")
    
    def abrir_archivo_log(self):
        """Abrir el archivo de log con el editor predeterminado"""
        try:
            log_file = self.error_logger.get_log_file_path()
            
            if not os.path.exists(log_file):
                messagebox.showwarning("Archivo no encontrado", 
                                     "No se encontró el archivo de log")
                return
            
            # Abrir con el editor predeterminado del sistema
            import platform
            if platform.system() == 'Windows':
                os.startfile(log_file)
            elif platform.system() == 'Darwin':  # macOS
                os.system(f'open "{log_file}"')
            else:  # Linux
                os.system(f'xdg-open "{log_file}"')
            
            messagebox.showinfo("Éxito", f"Archivo de log abierto:\n{log_file}")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
            from utils.error_logger import log_exception
            log_exception(e, context={
                'usuario': self.user_data.get('usuario', 'desconocido'),
                'vista': 'ErroresView',
                'accion': 'abrir_archivo_log'
            })
    
    def limpiar_logs(self):
        """Limpiar logs antiguos (con confirmación)"""
        try:
            respuesta = messagebox.askyesno(
                "Confirmar Limpieza",
                "¿Está seguro de que desea limpiar los logs de errores?\n\n"
                "Se creará un backup automáticamente antes de limpiar.\n\n"
                "Esta acción no se puede deshacer.",
                icon='warning'
            )
            
            if not respuesta:
                return
            
            # Limpiar logs
            success = self.error_logger.clear_old_errors()
            
            if success:
                messagebox.showinfo("Éxito", 
                                  "Logs limpiados correctamente.\n"
                                  "Se ha creado un backup automático.")
                self.cargar_errores()
            else:
                messagebox.showerror("Error", "No se pudieron limpiar los logs")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar logs: {e}")
            from utils.error_logger import log_exception
            log_exception(e, context={
                'usuario': self.user_data.get('usuario', 'desconocido'),
                'vista': 'ErroresView',
                'accion': 'limpiar_logs'
            })

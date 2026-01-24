import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models.configuracion import Configuracion
from models.backup import Backup
from utils.updater import UpdateManager
import os
from PIL import Image, ImageTk
import shutil

class ConfiguracionView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.config_model = Configuracion(db_manager)
        self.backup_model = Backup(db_manager)
        
        # Inicializar UpdateManager para búsqueda manual
        if getattr(__import__('sys'), 'frozen', False):
            base_path = os.path.dirname(__import__('sys').executable)
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.update_manager = UpdateManager(base_path)
        
        # Variables
        self.nombre_var = tk.StringVar()
        self.logo_path_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        self.cuit_var = tk.StringVar()
        self.logo_image = None
        
        self.create_widgets()
        self.cargar_configuracion()
    
    def create_widgets(self):
        """Crear widgets"""
        # Limpiar frame
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.parent.configure(bg='#F0F4F8')
        
        # Título
        title_frame = tk.Frame(self.parent, bg='#6366F1', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="⚙️ CONFIGURACIÓN DEL SISTEMA",
                font=("Arial", 18, "bold"),
                bg='#6366F1',
                fg='white').pack(expand=True)
        
        # Contenedor principal con scroll
        main_frame = tk.Frame(self.parent, bg='#F0F4F8')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Canvas y scrollbar para scroll vertical en todo el contenido
        canvas = tk.Canvas(main_frame, bg='#F0F4F8', highlightthickness=0)
        scrollbar_main = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_main.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.config(yscrollcommand=scrollbar_main.set)
        
        # Frame dentro del canvas
        main_container = tk.Frame(canvas, bg='#F0F4F8')
        canvas.create_window((0, 0), window=main_container, anchor=tk.NW)
        
        # Actualizar scroll region
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))
        
        main_container.bind('<Configure>', on_frame_configure)
        
        # Permitir scroll con rueda del mouse
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Notebook para tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.X)
        
        # Tab 0: Acerca de
        about_tab = tk.Frame(notebook, bg='#F0F4F8')
        notebook.add(about_tab, text="Acerca de")
        
        # Frame principal de acerca de
        about_container = tk.Frame(about_tab, bg='#F0F4F8')
        about_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Nombre del sistema
        about_header = tk.Frame(about_container, bg='white', relief=tk.RIDGE, bd=1, padx=20, pady=30)
        about_header.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(about_header,
                text="💼 SISTEMA DE VENTAS",
                font=("Arial", 20, "bold"),
                bg='white',
                fg='#2563EB').pack(pady=10)
        
        tk.Label(about_header,
                text="Gestión completa de ventas, inventario y reportes",
                font=("Arial", 11),
                bg='white',
                fg='#6B7280').pack(pady=5)
        
        # Información del sistema
        info_frame = tk.Frame(about_container, bg='white', relief=tk.RIDGE, bd=1, padx=20, pady=20)
        info_frame.pack(fill=tk.X, pady=10)
        
        # Versión
        tk.Label(info_frame,
                text="Versión:",
                font=("Arial", 11, "bold"),
                bg='white',
                fg='#374151').grid(row=0, column=0, sticky=tk.W, pady=8, padx=10)
        tk.Label(info_frame,
                text=f"v{self.update_manager.current_version}",
                font=("Arial", 11),
                bg='white',
                fg='#2563EB').grid(row=0, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Desarrollador
        tk.Label(info_frame,
                text="Desarrollador:",
                font=("Arial", 11, "bold"),
                bg='white',
                fg='#374151').grid(row=1, column=0, sticky=tk.W, pady=8, padx=10)
        tk.Label(info_frame,
                text="Digital&Servicios",
                font=("Arial", 11),
                bg='white',
                fg='#1F2937').grid(row=1, column=1, sticky=tk.W, pady=8, padx=10)
        
        # Descripción
        tk.Label(info_frame,
                text="Descripción:",
                font=("Arial", 11, "bold"),
                bg='white',
                fg='#374151').grid(row=2, column=0, sticky=tk.NW, pady=8, padx=10)
        
        desc_text = tk.Text(info_frame,
                           height=4,
                           width=60,
                           font=("Arial", 10),
                           bg='#F9FAFB',
                           relief=tk.RIDGE,
                           bd=1,
                           wrap=tk.WORD)
        desc_text.grid(row=2, column=1, sticky=tk.NSEW, pady=8, padx=10)
        
        desc_content = """Sistema integral de gestión de ventas con control de inventario, 
registro de productos y proveedores, generación de reportes y 
actualizaciones automáticas. Diseñado para pequeños y medianos negocios."""
        
        desc_text.insert(1.0, desc_content)
        desc_text.config(state=tk.DISABLED)
        
        # Información de licencia
        license_frame = tk.Frame(about_container, bg='white', relief=tk.RIDGE, bd=1, padx=20, pady=20)
        license_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(license_frame,
                text="🔐 Estado de Licencia:",
                font=("Arial", 12, "bold"),
                bg='white',
                fg='#10B981').pack(anchor=tk.W, pady=10)
        
        # Obtener estado de licencia
        try:
            from utils.validador_public import ValidadorLicencias
            validador = ValidadorLicencias()
            resultado = validador.validar_licencia()
            
            if resultado['valido']:
                dias = resultado['dias_restantes']
                if dias == -1:
                    status_text = "✓ Sistema Activado (Licencia Permanente)"
                    status_color = '#10B981'
                elif dias <= 30:
                    status_text = f"⚠️ Sistema Activado - Quedan {dias} días"
                    status_color = '#F59E0B'
                else:
                    status_text = f"✓ Sistema Activado - Quedan {dias} días"
                    status_color = '#10B981'
                
                tk.Label(license_frame,
                        text=status_text,
                        font=("Arial", 11, "bold"),
                        bg='white',
                        fg=status_color).pack(anchor=tk.W, pady=5, padx=10)
                
                if 'cliente' in resultado and resultado['cliente'] != 'N/A':
                    tk.Label(license_frame,
                            text=f"Licenciado a: {resultado['cliente']}",
                            font=("Arial", 10),
                            bg='white',
                            fg='#6B7280').pack(anchor=tk.W, pady=3, padx=10)
                
                if 'fecha_vencimiento' in resultado:
                    tk.Label(license_frame,
                            text=f"Vencimiento: {resultado['fecha_vencimiento']}",
                            font=("Arial", 10),
                            bg='white',
                            fg='#6B7280').pack(anchor=tk.W, pady=3, padx=10)
            else:
                tk.Label(license_frame,
                        text="❌ Licencia no válida",
                        font=("Arial", 11, "bold"),
                        bg='white',
                        fg='#EF4444').pack(anchor=tk.W, pady=5, padx=10)
                
                tk.Label(license_frame,
                        text=resultado.get('mensaje', 'Error desconocido'),
                        font=("Arial", 10),
                        bg='white',
                        fg='#6B7280').pack(anchor=tk.W, pady=3, padx=10)
        except Exception as e:
            tk.Label(license_frame,
                    text=f"⚠️ No se pudo verificar la licencia: {str(e)}",
                    font=("Arial", 10),
                    bg='white',
                    fg='#F59E0B').pack(anchor=tk.W, pady=5, padx=10)
        
        # Características
        features_frame = tk.Frame(about_container, bg='white', relief=tk.RIDGE, bd=1, padx=20, pady=20)
        features_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(features_frame,
                text="✨ Características Principales:",
                font=("Arial", 12, "bold"),
                bg='white',
                fg='#2563EB').pack(anchor=tk.W, pady=10)
        
        features = [
            "✓ Gestión completa de ventas y facturas",
            "✓ Control de inventario y stock",
            "✓ Registro de productos y proveedores",
            "✓ Sistema de usuarios con roles (Admin/Empleado)",
            "✓ Reportes y estadísticas de ventas",
            "✓ Copias de seguridad automáticas y manuales",
            "✓ Actualizaciones automáticas desde GitHub"
        ]
        
        for feature in features:
            tk.Label(features_frame,
                    text=feature,
                    font=("Arial", 10),
                    bg='white',
                    fg='#374151').pack(anchor=tk.W, pady=3, padx=10)
        
        # Licencia y tecnologías
        tech_frame = tk.Frame(about_container, bg='white', relief=tk.RIDGE, bd=1, padx=20, pady=20)
        tech_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(tech_frame,
                text="🛠️ Tecnologías Utilizadas:",
                font=("Arial", 12, "bold"),
                bg='white',
                fg='#6366F1').pack(anchor=tk.W, pady=10)
        
        tk.Label(tech_frame,
                text="Python 3.13 • Tkinter • SQLite • PIL • ReportLab",
                font=("Arial", 10),
                bg='white',
                fg='#374151').pack(anchor=tk.W, pady=5, padx=10)
        
        tk.Label(tech_frame,
                text="Licencia: MIT (Libre para uso comercial)",
                font=("Arial", 10),
                bg='white',
                fg='#374151').pack(anchor=tk.W, pady=5, padx=10)
        
        # Footer
        footer_frame = tk.Frame(about_container, bg='#F0F4F8')
        footer_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(footer_frame,
                text="© 2025-2026 Digital&Servicios. Todos los derechos reservados.",
                font=("Arial", 9),
                bg='#F0F4F8',
                fg='#9CA3AF').pack(pady=5)
        
        # Tab 1: Actualizaciones (DESHABILITADA)
        # updates_tab = tk.Frame(notebook, bg='#F0F4F8')
        # notebook.add(updates_tab, text="Actualizaciones")
        # # Frame de actualizaciones
        # updates_frame = tk.Frame(updates_tab, bg='white', relief=tk.RIDGE, bd=1, padx=20, pady=20)
        # updates_frame.pack(fill=tk.X, padx=15, pady=15)
        # tk.Label(updates_frame,
        #         text="🔄 Buscar Actualizaciones",
        #         font=("Arial", 13, "bold"),
        #         bg='white',
        #         fg='black').pack(anchor=tk.W, pady=10)
        # tk.Label(updates_frame,
        #         text="Verifica si hay una nueva versión disponible en GitHub.\n"
        #              "Tus datos NO se perderán durante la actualización.",
        #         font=("Arial", 10),
        #         bg='white',
        #         fg='#6B7280').pack(anchor=tk.W, pady=5)
        # info_frame = tk.Frame(updates_frame, bg='#F0F4F8', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        # info_frame.pack(fill=tk.X, pady=15)
        # tk.Label(info_frame,
        #         text=f"Versión actual: {self.update_manager.current_version}",
        #         font=("Arial", 10),
        #         bg='#F0F4F8',
        #         fg='#374151').pack(anchor=tk.W, pady=5)
        # self.update_status_label = tk.Label(info_frame,
        #                                    text="",
        #                                    font=("Arial", 9),
        #                                    bg='#F0F4F8',
        #                                    fg='#3B82F6')
        # self.update_status_label.pack(anchor=tk.W, pady=5)
        # tk.Button(updates_frame,
        #          text="🔍 Buscar Actualizaciones",
        #          font=('Arial', 12, 'bold'),
        #          bg='#3B82F6',
        #          fg='white',
        #          activebackground='#2563EB',
        #          bd=0,
        #          pady=12,
        #          cursor='hand2',
        #          command=self.buscar_actualizaciones).pack(pady=15, ipadx=30)
        
        # Tab 2: Personalización
        config_tab = tk.Frame(notebook, bg='#F0F4F8')
        notebook.add(config_tab, text="Personalización")
        
        # Frame de configuración
        config_frame = tk.Frame(config_tab, bg='white', relief=tk.RIDGE, bd=1, padx=20, pady=20)
        config_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Nombre del sistema
        tk.Label(config_frame, 
                 text="Nombre del Sistema:",
                 font=("Arial", 11, "bold"),
                 bg='white',
                 fg='black').grid(row=0, column=0, sticky=tk.W, pady=10, padx=5)
        
        nombre_entry = ttk.Entry(config_frame, 
                                textvariable=self.nombre_var,
                                font=("Arial", 11),
                                width=40)
        nombre_entry.grid(row=0, column=1, sticky=tk.EW, pady=10, padx=5)
        
        # Logo
        tk.Label(config_frame, 
                 text="Logo del Sistema:",
                 font=("Arial", 11, "bold"),
                 bg='white',
                 fg='black').grid(row=1, column=0, sticky=tk.W, pady=10, padx=5)
        
        logo_frame = tk.Frame(config_frame, bg='white')
        logo_frame.grid(row=1, column=1, sticky=tk.EW, pady=10, padx=5)
        
        ttk.Button(logo_frame,
                  text="📁 Seleccionar Logo",
                  command=self.seleccionar_logo).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(logo_frame,
                  text="❌ Quitar Logo",
                  command=self.quitar_logo).pack(side=tk.LEFT, padx=5)
        
        # Vista previa del logo
        tk.Label(config_frame,
                 text="Vista Previa:",
                 font=("Arial", 11, "bold"),
                 bg='white',
                 fg='black').grid(row=2, column=0, sticky=tk.NW, pady=10, padx=5)
        
        self.preview_label = tk.Label(config_frame, 
                                     text="Sin logo",
                                     bg='#E5E7EB',
                                     width=30,
                                     height=12,
                                     relief=tk.RIDGE,
                                     bd=2,
                                     font=("Arial", 12))
        self.preview_label.grid(row=2, column=1, sticky=tk.NSEW, pady=10, padx=5)
        
        # Hacer la celda cuadrada
        config_frame.grid_rowconfigure(2, minsize=300)
        
        # Ruta del logo actual
        self.logo_info_label = tk.Label(config_frame,
                                        text="",
                                        font=("Arial", 9),
                                        bg='white',
                                        fg='#6B7280')
        self.logo_info_label.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        # Teléfono
        tk.Label(config_frame, 
                 text="Teléfono:",
                 font=("Arial", 11, "bold"),
                 bg='white',
                 fg='black').grid(row=4, column=0, sticky=tk.W, pady=10, padx=5)
        
        telefono_entry = ttk.Entry(config_frame, 
                                   textvariable=self.telefono_var,
                                   font=("Arial", 11),
                                   width=40)
        telefono_entry.grid(row=4, column=1, sticky=tk.EW, pady=10, padx=5)
        
        # Dirección
        tk.Label(config_frame, 
                 text="Dirección:",
                 font=("Arial", 11, "bold"),
                 bg='white',
                 fg='black').grid(row=5, column=0, sticky=tk.W, pady=10, padx=5)
        
        direccion_entry = ttk.Entry(config_frame, 
                                    textvariable=self.direccion_var,
                                    font=("Arial", 11),
                                    width=40)
        direccion_entry.grid(row=5, column=1, sticky=tk.EW, pady=10, padx=5)
        
        # CUIT
        tk.Label(config_frame, 
                 text="CUIT:",
                 font=("Arial", 11, "bold"),
                 bg='white',
                 fg='black').grid(row=6, column=0, sticky=tk.W, pady=10, padx=5)
        
        cuit_entry = ttk.Entry(config_frame, 
                               textvariable=self.cuit_var,
                               font=("Arial", 11),
                               width=40)
        cuit_entry.grid(row=6, column=1, sticky=tk.EW, pady=10, padx=5)
        
        # Configurar expansión de columna
        config_frame.grid_columnconfigure(1, weight=1)
        
        # Botones de acción para personalización
        buttons_frame = tk.Frame(config_tab, bg='#F0F4F8')
        buttons_frame.pack(fill=tk.X, pady=20, padx=20)
        
        tk.Button(buttons_frame,
                 text="💾 Guardar Cambios",
                 font=('Arial', 11, 'bold'),
                 bg='#10B981',
                 fg='white',
                 activebackground='#059669',
                 bd=0,
                 pady=10,
                 cursor='hand2',
                 command=self.guardar_configuracion).pack(side=tk.LEFT, padx=5, ipadx=20)
        
        tk.Button(buttons_frame,
                 text="🔄 Restablecer",
                 font=('Arial', 11, 'bold'),
                 bg='#F59E0B',
                 fg='white',
                 activebackground='#D97706',
                 bd=0,
                 pady=10,
                 cursor='hand2',
                 command=self.cargar_configuracion).pack(side=tk.LEFT, padx=5, ipadx=20)
        
        # Tab 3: Copias de Seguridad
        backup_tab = tk.Frame(notebook, bg='#F0F4F8')
        notebook.add(backup_tab, text="Copias de Seguridad")
        
        # Contenedor para backup
        backup_container = tk.Frame(backup_tab, bg='#F0F4F8')
        backup_container.pack(fill=tk.X, padx=20, pady=20)
        
        # Frame de creación de backup
        create_backup_frame = tk.Frame(backup_container, bg='white', relief=tk.RIDGE, bd=1, padx=15, pady=15)
        create_backup_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(create_backup_frame,
                text="Crear una copia de seguridad completa de todos los datos:",
                font=("Arial", 10),
                bg='white',
                fg='black').pack(anchor=tk.W, pady=10)
        
        tk.Button(create_backup_frame,
                 text="💾 Crear Copia de Seguridad",
                 font=('Arial', 11, 'bold'),
                 bg='#10B981',
                 fg='white',
                 activebackground='#059669',
                 bd=0,
                 pady=12,
                 cursor='hand2',
                 width=40,
                 command=self.crear_backup).pack(pady=10)
        
        # Frame de restauración de backup
        restore_backup_frame = tk.Frame(backup_container, bg='white', relief=tk.RIDGE, bd=1, padx=15, pady=15)
        restore_backup_frame.pack(fill=tk.X)
        
        tk.Label(restore_backup_frame,
                text="Cargar una copia de seguridad anterior:",
                font=("Arial", 10),
                bg='white',
                fg='black').pack(anchor=tk.W, pady=10)
        
        restore_buttons = tk.Frame(restore_backup_frame, bg='white')
        restore_buttons.pack(fill=tk.X, pady=10)
        
        tk.Button(restore_buttons,
                 text="📂 Seleccionar Backup",
                 font=('Arial', 11, 'bold'),
                 bg='#3B82F6',
                 fg='white',
                 activebackground='#2563EB',
                 bd=0,
                 pady=12,
                 cursor='hand2',
                 width=30,
                 command=self.seleccionar_backup).pack(side=tk.LEFT, padx=5)
        
        tk.Button(restore_buttons,
                 text="♻️ Restaurar",
                 font=('Arial', 11, 'bold'),
                 bg='#8B5CF6',
                 fg='white',
                 activebackground='#7C3AED',
                 bd=0,
                 pady=12,
                 cursor='hand2',
                 width=20,
                 command=self.restaurar_backup).pack(side=tk.LEFT, padx=5)
        
        # Info del backup seleccionado
        self.backup_info_frame = tk.Frame(restore_backup_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        self.backup_info_frame.pack(fill=tk.X, pady=10)
        
        self.backup_info_text = tk.Text(self.backup_info_frame, 
                                       height=8, 
                                       width=50,
                                       font=("Courier", 9),
                                       bg='#F9FAFB',
                                       relief=tk.RIDGE,
                                       bd=1)
        self.backup_info_text.pack(fill=tk.BOTH, expand=True)
        self.backup_info_text.config(state=tk.DISABLED)
        
        # Variable para almacenar ruta del backup
        self.backup_path_var = tk.StringVar()
    
    def cargar_configuracion(self):
        """Cargar configuración actual"""
        config = self.config_model.obtener_configuracion()
        
        self.nombre_var.set(config.get('nombre_sistema', 'SISTEMA DE VENTAS'))
        self.telefono_var.set(config.get('telefono', '') or '')
        self.direccion_var.set(config.get('direccion', '') or '')
        self.cuit_var.set(config.get('cuit', '') or '')
        
        logo_path = config.get('logo_path')
        
        if logo_path and os.path.exists(logo_path):
            self.logo_path_var.set(logo_path)
            self.mostrar_preview(logo_path)
            self.logo_info_label.config(text=f"Archivo: {os.path.basename(logo_path)}")
        else:
            self.logo_path_var.set('')
            self.preview_label.config(image='', text='Sin logo')
            self.logo_info_label.config(text='')
    
    def seleccionar_logo(self):
        """Seleccionar archivo de logo"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Logo",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.logo_path_var.set(file_path)
            self.mostrar_preview(file_path)
            self.logo_info_label.config(text=f"Archivo: {os.path.basename(file_path)}")
    
    def quitar_logo(self):
        """Quitar logo"""
        self.logo_path_var.set('')
        self.preview_label.config(image='', text='Sin logo')
        self.logo_info_label.config(text='')
        self.logo_image = None
    
    def mostrar_preview(self, image_path):
        """Mostrar vista previa del logo"""
        try:
            image = Image.open(image_path)
            # Redimensionar manteniendo proporción
            image.thumbnail((200, 120), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(image)
            self.preview_label.config(image=self.logo_image, text='')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{str(e)}")
            self.logo_path_var.set('')
            self.logo_info_label.config(text='')
    
    def guardar_configuracion(self):
        """Guardar configuración"""
        nombre = self.nombre_var.get().strip()
        
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre del sistema no puede estar vacío")
            return
        
        logo_path = self.logo_path_var.get()
        telefono = self.telefono_var.get().strip()
        direccion = self.direccion_var.get().strip()
        cuit = self.cuit_var.get().strip()
        
        # Si hay un logo, copiarlo a la carpeta assets
        if logo_path and os.path.exists(logo_path):
            try:
                # Crear carpeta assets si no existe
                assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
                os.makedirs(assets_dir, exist_ok=True)
                
                # Copiar logo con nombre fijo
                ext = os.path.splitext(logo_path)[1]
                new_logo_path = os.path.join(assets_dir, f'logo{ext}')
                
                # Si es diferente archivo, copiarlo
                if os.path.abspath(logo_path) != os.path.abspath(new_logo_path):
                    shutil.copy2(logo_path, new_logo_path)
                
                logo_path = new_logo_path
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo copiar el logo:\n{str(e)}")
                return
        
        # Guardar configuración
        if self.config_model.actualizar_configuracion(nombre, logo_path, telefono, direccion, cuit):
            messagebox.showinfo("Éxito", "Configuración guardada correctamente.\n\nReinicie la aplicación para ver los cambios.")
        else:
            messagebox.showerror("Error", "No se pudo guardar la configuración")
    
    def crear_backup(self):
        """Crear copia de seguridad"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta para guardar el backup")
        
        if not folder:
            return
        
        success, result = self.backup_model.crear_backup(folder)
        
        if success:
            messagebox.showinfo("Éxito", f"Copia de seguridad creada:\n\n{result}")
        else:
            messagebox.showerror("Error", f"No se pudo crear el backup:\n{result}")
    
    def seleccionar_backup(self):
        """Seleccionar archivo de backup"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de backup",
            filetypes=[("Base de Datos", "*.db"), ("Todos", "*.*")]
        )
        
        if file_path:
            self.backup_path_var.set(file_path)
            self.mostrar_info_backup(file_path)
    
    def mostrar_info_backup(self, backup_path):
        """Mostrar información del backup"""
        info = self.backup_model.obtener_info_backup(backup_path)
        
        if info:
            self.backup_info_text.config(state=tk.NORMAL)
            self.backup_info_text.delete(1.0, tk.END)
            
            texto = f"""
INFORMACIÓN DEL BACKUP
{'='*45}

Archivo: {info['nombre']}
Tamaño: {info['tamaño']}
Fecha: {info['fecha']}

DATOS INCLUIDOS:
{'='*45}
✓ Usuarios: {info['usuarios']} registros
✓ Productos: {info['productos']} registros
✓ Proveedores: {info['proveedores']} registros
✓ Categorías: {info['categorias']} registros
✓ Ventas: {info['ventas']} registros
✓ Detalles Venta: {info['detalles_venta']} registros
            """
            
            self.backup_info_text.insert(1.0, texto)
            self.backup_info_text.config(state=tk.DISABLED)
        else:
            messagebox.showerror("Error", "No se pudo leer la información del backup")
    
    def restaurar_backup(self):
        """Restaurar backup"""
        backup_path = self.backup_path_var.get()
        
        if not backup_path:
            messagebox.showwarning("Advertencia", "Por favor selecciona un backup primero")
            return
        
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas restaurar el backup?\n\nEsto reemplazará todos los datos actuales."):
            success, message = self.backup_model.restaurar_backup(backup_path)
            
            if success:
                messagebox.showinfo("Éxito", message + "\n\nReinicie la aplicación para completar el proceso.")
            else:
                messagebox.showerror("Error", message)
    
    def buscar_actualizaciones(self):
        """Buscar actualizaciones manualmente"""
        # Deshabilitar botón mientras busca
        for widget in self.parent.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(state=tk.DISABLED)
        
        self.update_status_label.config(text="Buscando actualizaciones...", fg='#3B82F6')
        self.parent.update()
        
        try:
            # Buscar actualizaciones (forzar búsqueda manual)
            actualizar_disponible, error_msg = self.update_manager.check_for_updates(force=True)
            
            if error_msg:
                # Hay un error específico
                self.update_status_label.config(text=f"⚠ {error_msg}", fg='#F59E0B')
                
                if "No hay releases" in error_msg:
                    messagebox.showinfo(
                        "Sin Releases",
                        f"No hay actualizaciones publicadas en GitHub todavía.\n\n"
                        f"Versión actual: v{self.update_manager.current_version}\n\n"
                        f"Para publicar una actualización:\n"
                        f"1. Crea un tag: git tag v1.0.1\n"
                        f"2. Sube el tag: git push origin v1.0.1\n"
                        f"3. Crea un Release en GitHub con ese tag"
                    )
                else:
                    messagebox.showerror("Error de Conexión", f"{error_msg}\n\nVerifica tu conexión a Internet.")
                
            elif actualizar_disponible:
                config = self.update_manager.get_update_config()
                latest_version = config.get("latest_version", "?")
                release_notes = config.get("release_notes", "Sin descripción disponible")
                
                self.update_status_label.config(
                    text=f"✓ Actualización disponible: v{latest_version}",
                    fg='#10B981'
                )
                
                # Crear ventana de detalles
                detalle_msg = (
                    f"Se encontró una nueva versión: v{latest_version}\n"
                    f"Versión actual: v{self.update_manager.current_version}\n\n"
                    f"📝 Notas de la actualización:\n"
                    f"{release_notes[:300]}{'...' if len(release_notes) > 300 else ''}\n\n"
                    f"✓ Tus datos y base de datos NO serán eliminados\n\n"
                    f"¿Deseas instalar la actualización ahora?"
                )
                
                resultado = messagebox.askyesno(
                    "Actualización Disponible",
                    detalle_msg
                )
                
                if resultado:
                    self.update_status_label.config(text="Instalando actualización...", fg='#F59E0B')
                    self.parent.update()
                    
                    if self.update_manager.perform_update():
                        # El reinicio es automático en perform_update
                        pass
                    else:
                        self.update_status_label.config(text="Error en la actualización", fg='#EF4444')
            else:
                self.update_status_label.config(
                    text="✓ Tu versión está actualizada",
                    fg='#10B981'
                )
                messagebox.showinfo(
                    "Sin Actualizaciones",
                    f"Ya tienes la versión más reciente (v{self.update_manager.current_version})\n\n"
                    f"Última verificación: ahora"
                )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.update_status_label.config(
                text=f"Error en la actualización",
                fg='#EF4444'
            )
            messagebox.showerror(
                "Error", 
                f"No se pudo verificar las actualizaciones:\n\n{str(e)}\n\n"
                f"Detalles técnicos:\n{error_details[:500]}"
            )
        finally:
            # Habilitar botón nuevamente
            for widget in self.parent.winfo_children():
                if isinstance(widget, tk.Button):
                    widget.config(state=tk.NORMAL)

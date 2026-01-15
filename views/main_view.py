import tkinter as tk
from tkinter import ttk, messagebox
from views.ventas_view import VentasView
from views.productos_view import ProductosView
from views.proveedores_view import ProveedoresView
from views.reportes_view import ReportesView
from views.usuarios_view import UsuariosView
from views.configuracion_view import ConfiguracionView

class MainView:
    def __init__(self, root, db_manager, user_data, logout_callback=None):
        self.root = root
        self.db_manager = db_manager
        self.user_data = user_data
        self.logout_callback = logout_callback
        
        self.root.title(f"Sistema de Ventas - {user_data['nombre_completo']} ({user_data['rol'].upper()})")
        self.root.geometry("1200x700")
        
        # Configurar estilo
        self.setup_styles()
        
        self.create_widgets()
        
        # Maximizar ventana
        self.root.state('zoomed')
    
    def setup_styles(self):
        """Configurar estilos personalizados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores del tema
        bg_color = '#F0F4F8'
        primary_color = '#2563EB'  # Azul
        secondary_color = '#10B981'  # Verde
        
        # Configurar colores de fondo
        self.root.configure(bg=bg_color)
        
        # Estilos para frames
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background='white', borderwidth=2)
        
        # Estilos para botones
        style.configure('Menu.TButton', font=('Arial', 10), padding=10)
    
    def create_widgets(self):
        """Crear widgets de la interfaz principal"""
        # Frame superior (barra de título)
        top_frame = tk.Frame(self.root, bg='#1F2937', height=50)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        top_frame.pack_propagate(False)
        
        tk.Label(top_frame, 
                text=f"👤 {self.user_data['nombre_completo']}", 
                font=("Arial", 11, "bold"),
                bg='#1F2937',
                fg='white').pack(side=tk.LEFT, padx=15, pady=5)
        
        role_color = '#10B981' if self.user_data['rol'] == 'admin' else '#3B82F6'
        tk.Label(top_frame, 
                text=f"🔑 {self.user_data['rol'].upper()}", 
                font=("Arial", 10, "bold"),
                bg='#1F2937',
                fg=role_color).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Botón de cerrar sesión
        logout_btn = tk.Button(top_frame, 
                              text="🚪 Cerrar Sesión",
                              font=('Arial', 9, 'bold'),
                              bg='#EF4444',
                              fg='white',
                              activebackground='#DC2626',
                              activeforeground='white',
                              bd=0,
                              padx=15,
                              pady=8,
                              cursor='hand2',
                              command=self.logout)
        logout_btn.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Frame lateral (menú)
        side_frame = tk.Frame(self.root, width=220, bg='#374151')
        side_frame.pack(side=tk.LEFT, fill=tk.Y)
        side_frame.pack_propagate(False)
        
        # Título del menú
        menu_title = tk.Label(side_frame, 
                             text="📋 MENÚ", 
                             font=("Arial", 14, "bold"),
                             bg='#374151',
                             fg='white',
                             pady=20)
        menu_title.pack(fill=tk.X)
        
        # Separador
        tk.Frame(side_frame, height=2, bg='#4B5563').pack(fill=tk.X, padx=10, pady=5)
        
        # Botones del menú con iconos
        menu_buttons = [
            ("💰 Nueva Venta", self.mostrar_ventas, '#10B981'),
            ("📦 Productos", self.mostrar_productos, '#3B82F6'),
            ("🏢 Proveedores", self.mostrar_proveedores, '#8B5CF6'),
            ("📊 Reportes", self.mostrar_reportes, '#F59E0B'),
        ]
        
        for text, command, color in menu_buttons:
            btn = tk.Button(side_frame,
                          text=text,
                          font=('Arial', 11, 'bold'),
                          bg=color,
                          fg='white',
                          activebackground=color,
                          activeforeground='white',
                          bd=0,
                          pady=12,
                          cursor='hand2',
                          command=command)
            btn.pack(fill=tk.X, padx=12, pady=6)
        
        # Solo admin puede gestionar usuarios
        if self.user_data['rol'] == 'admin':
            admin_btn = tk.Button(side_frame,
                                 text="👥 Usuarios",
                                 font=('Arial', 11, 'bold'),
                                 bg='#EC4899',
                                 fg='white',
                                 activebackground='#DB2777',
                                 activeforeground='white',
                                 bd=0,
                                 pady=12,
                                 cursor='hand2',
                                 command=self.mostrar_usuarios)
            admin_btn.pack(fill=tk.X, padx=12, pady=6)
            
            config_btn = tk.Button(side_frame,
                                  text="⚙️ Configuración",
                                  font=('Arial', 11, 'bold'),
                                  bg='#6366F1',
                                  fg='white',
                                  activebackground='#4F46E5',
                                  activeforeground='white',
                                  bd=0,
                                  pady=12,
                                  cursor='hand2',
                                  command=self.mostrar_configuracion)
            config_btn.pack(fill=tk.X, padx=12, pady=6)
        
        # Frame de contenido
        self.content_frame = tk.Frame(self.root, bg='#F0F4F8')
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Mostrar vista inicial
        self.mostrar_ventas()
    
    def limpiar_contenido(self):
        """Limpiar el frame de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def mostrar_ventas(self):
        """Mostrar vista de ventas"""
        self.limpiar_contenido()
        VentasView(self.content_frame, self.db_manager, self.user_data)
    
    def mostrar_productos(self):
        """Mostrar vista de productos"""
        self.limpiar_contenido()
        ProductosView(self.content_frame, self.db_manager, self.user_data)
    
    def mostrar_proveedores(self):
        """Mostrar vista de proveedores"""
        self.limpiar_contenido()
        ProveedoresView(self.content_frame, self.db_manager, self.user_data)
    
    def mostrar_reportes(self):
        """Mostrar vista de reportes"""
        self.limpiar_contenido()
        ReportesView(self.content_frame, self.db_manager, self.user_data)
    
    def mostrar_usuarios(self):
        """Mostrar vista de usuarios (solo admin)"""
        if self.user_data['rol'] == 'admin':
            self.limpiar_contenido()
            UsuariosView(self.content_frame, self.db_manager, self.user_data)
    
    def mostrar_configuracion(self):
        """Mostrar vista de configuración (solo admin)"""
        if self.user_data['rol'] == 'admin':
            self.limpiar_contenido()
            ConfiguracionView(self.content_frame, self.db_manager, self.user_data)
    
    def logout(self):
        """Cerrar sesión"""
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar sesión?"):
            if self.logout_callback:
                self.logout_callback()
            else:
                self.root.destroy()

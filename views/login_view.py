import tkinter as tk
from tkinter import ttk, messagebox
from models.usuario import Usuario
from models.configuracion import Configuracion
from PIL import Image, ImageTk
import os

class LoginView:
    def __init__(self, root, db_manager, on_login_success):
        self.root = root
        self.db_manager = db_manager
        self.on_login_success = on_login_success
        self.usuario_model = Usuario(db_manager)
        self.config_model = Configuracion(db_manager)
        
        # Obtener configuración
        self.config = self.config_model.obtener_configuracion()
        self.logo_image = None
        
        self.root.title("Sistema de Ventas - Login")
        self.root.geometry("450x320")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        self.create_widgets()
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crear widgets de la interfaz"""
        # Configurar fondo
        self.root.configure(bg='#F0F4F8')
        
        # Título con fondo azul
        title_frame = tk.Frame(self.root, bg='#2563EB', height=60)
        title_frame.pack(fill=tk.X, pady=0)
        title_frame.pack_propagate(False)
        
        # Contenedor para logo y título
        title_content = tk.Frame(title_frame, bg='#2563EB')
        title_content.pack(expand=True, fill=tk.BOTH)
        
        # Logo si existe
        logo_path = self.config.get('logo_path')
        if logo_path and os.path.exists(logo_path):
            try:
                image = Image.open(logo_path)
                image.thumbnail((40, 40), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(image)
                
                logo_label = tk.Label(title_content, 
                                     image=self.logo_image,
                                     bg='#2563EB')
                logo_label.pack(side=tk.LEFT, padx=(10, 5))
            except:
                pass
        
        # Título
        nombre_sistema = self.config.get('nombre_sistema', 'SISTEMA DE VENTAS')
        tk.Label(title_content,
                text=f"🏪 {nombre_sistema}",
                font=("Arial", 16, "bold"),
                bg='#2563EB',
                fg='white').pack(side=tk.LEFT, expand=True)
        
        # Frame central de login
        login_frame = tk.Frame(self.root, bg='#F0F4F8')
        login_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)
        
        # Usuario
        tk.Label(login_frame, 
                text="👤 Usuario:", 
                font=("Arial", 10),
                bg='#F0F4F8',
                fg='#374151').grid(row=0, column=0, sticky=tk.W, pady=(10, 3), padx=5)
        
        self.username_entry = ttk.Entry(login_frame, 
                                       width=30,
                                       font=("Arial", 10))
        self.username_entry.grid(row=1, column=0, pady=(0, 10), padx=5, sticky=tk.EW, ipady=4)
        
        # Contraseña
        tk.Label(login_frame, 
                text="🔒 Contraseña:", 
                font=("Arial", 10),
                bg='#F0F4F8',
                fg='#374151').grid(row=2, column=0, sticky=tk.W, pady=3, padx=5)
        
        self.password_entry = ttk.Entry(login_frame, 
                                       width=30, 
                                       show="*",
                                       font=("Arial", 10))
        self.password_entry.grid(row=3, column=0, pady=(0, 15), padx=5, sticky=tk.EW, ipady=4)
        
        # Frame para botones
        buttons_frame = tk.Frame(login_frame, bg='#F0F4F8')
        buttons_frame.grid(row=4, column=0, pady=(5, 10), padx=5, sticky=tk.EW)
        
        # Botón de login con color
        login_btn = tk.Button(buttons_frame, 
                             text="🔓 Iniciar Sesión",
                             font=('Arial', 9, 'bold'),
                             bg='#10B981',
                             fg='white',
                             activebackground='#059669',
                             activeforeground='white',
                             bd=0,
                             pady=8,
                             cursor='hand2',
                             command=self.login)
        login_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Botón de cerrar
        close_btn = tk.Button(buttons_frame, 
                            text="❌ Cerrar",
                            font=('Arial', 9, 'bold'),
                            bg='#EF4444',
                            fg='white',
                            activebackground='#DC2626',
                            activeforeground='white',
                            bd=0,
                            pady=8,
                            cursor='hand2',
                            command=self.root.quit)
        close_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Info por defecto
        # tk.Label(login_frame,
        #         text="ℹ️  Usuario por defecto: admin / admin123",
        #         font=("Arial", 8),
        #         bg='#F0F4F8',
        #         fg='#1E40AF').grid(row=5, column=0, pady=5)
        
        # Configurar expansión de columna
        login_frame.grid_columnconfigure(0, weight=1)
        
        # Bind Enter key
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Focus en username
        self.username_entry.focus()
    
    def login(self):
        """Procesar login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Por favor complete todos los campos")
            return
        
        user = self.usuario_model.autenticar(username, password)
        
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()

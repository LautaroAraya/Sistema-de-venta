import tkinter as tk
from tkinter import ttk, messagebox
from models.usuario import Usuario

class UsuariosView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.usuario_model = Usuario(db_manager)
        
        # Solo admin puede acceder
        if user_data['rol'] != 'admin':
            ttk.Label(parent, text="Acceso Denegado", 
                     font=("Arial", 16, "bold")).pack(pady=50)
            return
        
        self.create_widgets()
        self.cargar_usuarios()
    
    def create_widgets(self):
        """Crear widgets"""
        self.parent.configure(bg='#F0F4F8')
        
        # Título con color
        title_frame = tk.Frame(self.parent, bg='#EC4899', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="👥 GESTIÓN DE USUARIOS",
                font=("Arial", 18, "bold"),
                bg='#EC4899',
                fg='white').pack(expand=True)
        
        # Botones de acción
        buttons_frame = ttk.Frame(self.parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Nuevo Usuario", 
                  command=self.nuevo_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cambiar Contraseña", 
                  command=self.cambiar_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Actualizar", 
                  command=self.cargar_usuarios).pack(side=tk.LEFT, padx=5)
        
        # Tabla de usuarios
        columns = ('id', 'username', 'nombre', 'rol', 'fecha')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=20)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('username', text='Usuario')
        self.tree.heading('nombre', text='Nombre Completo')
        self.tree.heading('rol', text='Rol')
        self.tree.heading('fecha', text='Fecha Creación')
        
        self.tree.column('id', width=50)
        self.tree.column('username', width=150)
        self.tree.column('nombre', width=250)
        self.tree.column('rol', width=100)
        self.tree.column('fecha', width=150)
        
        # Scrollbar vertical
        scrollbar_v = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar_v.set)
        
        # Scrollbar horizontal
        scrollbar_h = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_h.pack(fill=tk.X)
        self.tree.config(xscrollcommand=scrollbar_h.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def cargar_usuarios(self):
        """Cargar usuarios en la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        usuarios = self.usuario_model.listar_usuarios()
        for user in usuarios:
            self.tree.insert('', tk.END, values=(
                user[0], user[1], user[2], user[3].upper(), user[4]
            ))
    
    def nuevo_usuario(self):
        """Nuevo usuario"""
        UsuarioDialog(self.parent, self.db_manager, self.cargar_usuarios)
    
    def cambiar_password(self):
        """Cambiar contraseña de usuario"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario")
            return
        
        item = self.tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        CambiarPasswordDialog(self.parent, self.db_manager, user_id, username)


class UsuarioDialog:
    def __init__(self, parent, db_manager, callback):
        self.db_manager = db_manager
        self.callback = callback
        self.usuario_model = Usuario(db_manager)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Usuario")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 200
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 150
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Username
        tk.Label(main_frame, text="Usuario:", bg='white', fg='black').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = tk.Entry(main_frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Nombre completo
        tk.Label(main_frame, text="Nombre Completo:", bg='white', fg='black').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.nombre_entry = tk.Entry(main_frame, width=25)
        self.nombre_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Contraseña
        tk.Label(main_frame, text="Contraseña:", bg='white', fg='black').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = tk.Entry(main_frame, width=25, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Confirmar contraseña
        tk.Label(main_frame, text="Confirmar:", bg='white', fg='black').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.confirm_entry = tk.Entry(main_frame, width=25, show="*")
        self.confirm_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # Rol
        tk.Label(main_frame, text="Rol:", bg='white', fg='black').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.rol_combo = ttk.Combobox(main_frame, width=23, state='readonly')
        self.rol_combo['values'] = ['admin', 'empleado']
        self.rol_combo.current(1)
        self.rol_combo.grid(row=4, column=1, pady=5, padx=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        tk.Button(buttons_frame, text="Guardar", font=('Arial', 10), bg='#10B981', fg='white', relief=tk.RAISED,
                  command=self.guardar).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=('Arial', 10), bg='#EF4444', fg='white', relief=tk.RAISED,
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def guardar(self):
        """Guardar usuario"""
        username = self.username_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        rol = self.rol_combo.get()
        
        if not username or not nombre or not password:
            messagebox.showerror("Error", "Complete todos los campos")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
            return
        
        exito, mensaje = self.usuario_model.crear_usuario(username, password, nombre, rol)
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", mensaje)


class CambiarPasswordDialog:
    def __init__(self, parent, db_manager, user_id, username):
        self.db_manager = db_manager
        self.user_id = user_id
        self.usuario_model = Usuario(db_manager)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Cambiar Contraseña - {username}")
        self.dialog.geometry("350x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 175
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 100
        self.dialog.geometry(f"350x200+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nueva contraseña
        tk.Label(main_frame, text="Nueva Contraseña:", bg='white', fg='black').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.password_entry = tk.Entry(main_frame, width=25, show="*")
        self.password_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Confirmar
        tk.Label(main_frame, text="Confirmar:", bg='white', fg='black').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.confirm_entry = tk.Entry(main_frame, width=25, show="*")
        self.confirm_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(buttons_frame, text="Guardar", font=('Arial', 10), bg='#10B981', fg='white', relief=tk.RAISED,
                  command=self.guardar).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=('Arial', 10), bg='#EF4444', fg='white', relief=tk.RAISED,
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def guardar(self):
        """Guardar nueva contraseña"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Ingrese la nueva contraseña")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres")
            return
        
        self.usuario_model.cambiar_password(self.user_id, password)
        messagebox.showinfo("Éxito", "Contraseña actualizada")
        self.dialog.destroy()

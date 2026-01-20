import tkinter as tk
from tkinter import ttk, messagebox
from models.proveedor import Proveedor

class ProveedoresView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.proveedor_model = Proveedor(db_manager)
        
        self.create_widgets()
        self.cargar_proveedores()
    
    def create_widgets(self):
        """Crear widgets"""
        self.parent.configure(bg='#F0F4F8')
        
        # Título con color
        title_frame = tk.Frame(self.parent, bg='#8B5CF6', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="🏢 GESTIÓN DE PROVEEDORES",
                font=("Arial", 18, "bold"),
                bg='#8B5CF6',
                fg='white').pack(expand=True)
        
        # Botones de acción
        buttons_frame = ttk.Frame(self.parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Permitir a empleados crear/editar/eliminar proveedores
        self.btn_nuevo = ttk.Button(buttons_frame, text="Nuevo Proveedor", 
              command=self.nuevo_proveedor)
        self.btn_nuevo.pack(side=tk.LEFT, padx=5)
        
        self.btn_editar = ttk.Button(buttons_frame, text="Editar", 
              command=self.editar_proveedor)
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        
        self.btn_eliminar = ttk.Button(buttons_frame, text="Eliminar", 
              command=self.eliminar_proveedor)
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Actualizar", 
                  command=self.cargar_proveedores).pack(side=tk.LEFT, padx=5)
        
        # Tabla de proveedores
        columns = ('id', 'nombre', 'contacto', 'telefono', 'email', 'direccion')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=20)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('contacto', text='Contacto')
        self.tree.heading('telefono', text='Teléfono')
        self.tree.heading('email', text='Email')
        self.tree.heading('direccion', text='Dirección')
        
        self.tree.column('id', width=50)
        self.tree.column('nombre', width=200)
        self.tree.column('contacto', width=150)
        self.tree.column('telefono', width=120)
        self.tree.column('email', width=200)
        self.tree.column('direccion', width=250)
        
        # Scrollbar vertical
        scrollbar_v = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar_v.set)
        
        # Scrollbar horizontal
        scrollbar_h = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_h.pack(fill=tk.X)
        self.tree.config(xscrollcommand=scrollbar_h.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def cargar_proveedores(self):
        """Cargar proveedores en la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        proveedores = self.proveedor_model.listar_proveedores()
        for prov in proveedores:
            self.tree.insert('', tk.END, values=(
                prov[0], prov[1], prov[2] or '-', prov[3] or '-', 
                prov[4] or '-', prov[5] or '-'
            ))
    
    def nuevo_proveedor(self):
        """Nuevo proveedor"""
        ProveedorDialog(self.parent, self.db_manager, None, self.cargar_proveedores)
    
    def editar_proveedor(self):
        """Editar proveedor"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor")
            return
        
        item = self.tree.item(selection[0])
        proveedor_id = item['values'][0]
        
        ProveedorDialog(self.parent, self.db_manager, proveedor_id, self.cargar_proveedores)
    
    def eliminar_proveedor(self):
        """Eliminar proveedor"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un proveedor")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este proveedor?"):
            item = self.tree.item(selection[0])
            proveedor_id = item['values'][0]
            
            self.proveedor_model.eliminar_proveedor(proveedor_id)
            messagebox.showinfo("Éxito", "Proveedor eliminado")
            self.cargar_proveedores()


class ProveedorDialog:
    def __init__(self, parent, db_manager, proveedor_id, callback):
        self.db_manager = db_manager
        self.proveedor_id = proveedor_id
        self.callback = callback
        self.proveedor_model = Proveedor(db_manager)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Proveedor" if proveedor_id is None else "Editar Proveedor")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 225
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 175
        self.dialog.geometry(f"450x350+{x}+{y}")
        
        self.create_widgets()
        
        if proveedor_id:
            self.cargar_datos()
    
    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Nombre
        tk.Label(main_frame, text="Nombre:", bg='white', fg='black').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nombre_entry = tk.Entry(main_frame, width=30)
        self.nombre_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Contacto
        tk.Label(main_frame, text="Contacto:", bg='white', fg='black').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.contacto_entry = tk.Entry(main_frame, width=30)
        self.contacto_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Teléfono
        tk.Label(main_frame, text="Teléfono:", bg='white', fg='black').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.telefono_entry = tk.Entry(main_frame, width=30)
        self.telefono_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Email
        tk.Label(main_frame, text="Email:", bg='white', fg='black').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.email_entry = tk.Entry(main_frame, width=30)
        self.email_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # Dirección
        tk.Label(main_frame, text="Dirección:", bg='white', fg='black').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.direccion_entry = tk.Entry(main_frame, width=30)
        self.direccion_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        tk.Button(buttons_frame, text="Guardar", font=('Arial', 10), bg='#10B981', fg='white', relief=tk.RAISED,
                  command=self.guardar).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=('Arial', 10), bg='#EF4444', fg='white', relief=tk.RAISED,
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def cargar_datos(self):
        """Cargar datos del proveedor"""
        proveedor = self.proveedor_model.obtener_proveedor_por_id(self.proveedor_id)
        if proveedor:
            self.nombre_entry.insert(0, proveedor[1])
            self.contacto_entry.insert(0, proveedor[2] or '')
            self.telefono_entry.insert(0, proveedor[3] or '')
            self.email_entry.insert(0, proveedor[4] or '')
            self.direccion_entry.insert(0, proveedor[5] or '')
    
    def guardar(self):
        """Guardar proveedor"""
        nombre = self.nombre_entry.get().strip()
        contacto = self.contacto_entry.get().strip()
        telefono = self.telefono_entry.get().strip()
        email = self.email_entry.get().strip()
        direccion = self.direccion_entry.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        if self.proveedor_id:
            exito, mensaje = self.proveedor_model.actualizar_proveedor(
                self.proveedor_id, nombre, contacto, telefono, email, direccion
            )
        else:
            exito, mensaje = self.proveedor_model.crear_proveedor(
                nombre, contacto, telefono, email, direccion
            )
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", mensaje)

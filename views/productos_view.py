import tkinter as tk
from tkinter import ttk, messagebox
from models.producto import Producto
from models.categoria import Categoria
from models.proveedor import Proveedor

class ProductosView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.producto_model = Producto(db_manager)
        self.categoria_model = Categoria(db_manager)
        self.proveedor_model = Proveedor(db_manager)
        
        self.create_widgets()
        self.cargar_productos()
    
    def create_widgets(self):
        """Crear widgets"""
        self.parent.configure(bg='#F0F4F8')
        
        # Título con color
        title_frame = tk.Frame(self.parent, bg='#3B82F6', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="📦 GESTIÓN DE PRODUCTOS",
                font=("Arial", 18, "bold"),
                bg='#3B82F6',
                fg='white').pack(expand=True)
        
        # Botones de acción
        buttons_frame = ttk.Frame(self.parent)
        buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Verificar si el usuario es empleado
        es_empleado = self.user_data['rol'] == 'empleado'
        
        self.btn_nuevo = ttk.Button(buttons_frame, text="Nuevo Producto", 
                  command=self.nuevo_producto, state='disabled' if es_empleado else 'normal')
        self.btn_nuevo.pack(side=tk.LEFT, padx=5)
        
        self.btn_editar = ttk.Button(buttons_frame, text="Editar", 
                  command=self.editar_producto, state='disabled' if es_empleado else 'normal')
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        
        self.btn_eliminar = ttk.Button(buttons_frame, text="Eliminar", 
                  command=self.eliminar_producto, state='disabled' if es_empleado else 'normal')
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Actualizar", 
                  command=self.cargar_productos).pack(side=tk.LEFT, padx=5)
        
        # Tabla de productos
        columns = ('id', 'codigo', 'nombre', 'categoria', 'precio', 'stock', 'proveedor')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=20)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('codigo', text='Código')
        self.tree.heading('nombre', text='Nombre')
        self.tree.heading('categoria', text='Categoría')
        self.tree.heading('precio', text='Precio')
        self.tree.heading('stock', text='Stock')
        self.tree.heading('proveedor', text='Proveedor')
        
        self.tree.column('id', width=50)
        self.tree.column('codigo', width=100)
        self.tree.column('nombre', width=250)
        self.tree.column('categoria', width=150)
        self.tree.column('precio', width=100)
        self.tree.column('stock', width=80)
        self.tree.column('proveedor', width=200)
        
        # Scrollbar vertical
        scrollbar_v = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar_v.set)
        
        # Scrollbar horizontal
        scrollbar_h = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_h.pack(fill=tk.X)
        self.tree.config(xscrollcommand=scrollbar_h.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def cargar_productos(self):
        """Cargar productos en la tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Cargar productos
        productos = self.producto_model.listar_productos()
        for prod in productos:
            self.tree.insert('', tk.END, values=(
                prod[0], prod[1], prod[2], prod[4] or '-', 
                f"${prod[5]:.2f}", prod[6], prod[7] or '-'
            ))
    
    def nuevo_producto(self):
        """Abrir ventana para nuevo producto"""
        ProductoDialog(self.parent, self.db_manager, None, self.cargar_productos)
    
    def editar_producto(self):
        """Editar producto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.tree.item(selection[0])
        producto_id = item['values'][0]
        
        ProductoDialog(self.parent, self.db_manager, producto_id, self.cargar_productos)
    
    def eliminar_producto(self):
        """Eliminar producto seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            item = self.tree.item(selection[0])
            producto_id = item['values'][0]
            
            self.producto_model.eliminar_producto(producto_id)
            messagebox.showinfo("Éxito", "Producto eliminado")
            self.cargar_productos()


class ProductoDialog:
    def __init__(self, parent, db_manager, producto_id, callback):
        self.db_manager = db_manager
        self.producto_id = producto_id
        self.callback = callback
        self.producto_model = Producto(db_manager)
        self.categoria_model = Categoria(db_manager)
        self.proveedor_model = Proveedor(db_manager)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nuevo Producto" if producto_id is None else "Editar Producto")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 225
        self.dialog.geometry(f"500x450+{x}+{y}")
        
        self.create_widgets()
        
        if producto_id:
            self.cargar_datos()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Código
        tk.Label(main_frame, text="Código:", bg='white', fg='black').grid(row=0, column=0, sticky=tk.W, pady=5)
        self.codigo_entry = tk.Entry(main_frame, width=30)
        self.codigo_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Nombre
        tk.Label(main_frame, text="Nombre:", bg='white', fg='black').grid(row=1, column=0, sticky=tk.W, pady=5)
        self.nombre_entry = tk.Entry(main_frame, width=30)
        self.nombre_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Descripción
        tk.Label(main_frame, text="Descripción:", bg='white', fg='black').grid(row=2, column=0, sticky=tk.W, pady=5)
        self.descripcion_entry = tk.Entry(main_frame, width=30)
        self.descripcion_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Categoría
        tk.Label(main_frame, text="Categoría:", bg='white', fg='black').grid(row=3, column=0, sticky=tk.W, pady=5)
        self.categoria_combo = ttk.Combobox(main_frame, width=28, state='readonly')
        self.categoria_combo.grid(row=3, column=1, pady=5, padx=5)
        
        # Cargar categorías
        categorias = self.categoria_model.listar_categorias()
        self.categoria_combo['values'] = [f"{cat[0]} - {cat[1]}" for cat in categorias]
        
        # Precio
        tk.Label(main_frame, text="Precio:", bg='white', fg='black').grid(row=4, column=0, sticky=tk.W, pady=5)
        self.precio_entry = tk.Entry(main_frame, width=30)
        self.precio_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Stock
        tk.Label(main_frame, text="Stock:", bg='white', fg='black').grid(row=5, column=0, sticky=tk.W, pady=5)
        self.stock_entry = tk.Entry(main_frame, width=30)
        self.stock_entry.grid(row=5, column=1, pady=5, padx=5)
        
        # Proveedor
        tk.Label(main_frame, text="Proveedor:", bg='white', fg='black').grid(row=6, column=0, sticky=tk.W, pady=5)
        self.proveedor_combo = ttk.Combobox(main_frame, width=28, state='readonly')
        self.proveedor_combo.grid(row=6, column=1, pady=5, padx=5)
        
        # Cargar proveedores
        proveedores = self.proveedor_model.listar_proveedores()
        self.proveedor_combo['values'] = [f"{prov[0]} - {prov[1]}" for prov in proveedores]
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        tk.Button(buttons_frame, text="Guardar", font=('Arial', 10), bg='#10B981', fg='white', relief=tk.RAISED,
                  command=self.guardar).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=('Arial', 10), bg='#EF4444', fg='white', relief=tk.RAISED,
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def cargar_datos(self):
        """Cargar datos del producto existente"""
        producto = self.producto_model.obtener_producto_por_id(self.producto_id)
        if producto:
            self.codigo_entry.insert(0, producto[1])
            self.nombre_entry.insert(0, producto[2])
            self.descripcion_entry.insert(0, producto[3] or '')
            self.precio_entry.insert(0, str(producto[5]))
            self.stock_entry.insert(0, str(producto[6]))
            
            # Seleccionar categoría
            if producto[4]:
                for i, val in enumerate(self.categoria_combo['values']):
                    if val.startswith(str(producto[4])):
                        self.categoria_combo.current(i)
                        break
            
            # Seleccionar proveedor
            if producto[7]:
                for i, val in enumerate(self.proveedor_combo['values']):
                    if val.startswith(str(producto[7])):
                        self.proveedor_combo.current(i)
                        break
    
    def guardar(self):
        """Guardar producto"""
        codigo = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        descripcion = self.descripcion_entry.get().strip()
        precio = self.precio_entry.get().strip()
        stock = self.stock_entry.get().strip()
        
        if not codigo or not nombre or not precio or not stock:
            messagebox.showerror("Error", "Complete los campos obligatorios")
            return
        
        try:
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Error", "Precio o stock inválido")
            return
        
        # Obtener IDs de categoría y proveedor
        categoria_id = None
        if self.categoria_combo.get():
            categoria_id = int(self.categoria_combo.get().split(' - ')[0])
        
        proveedor_id = None
        if self.proveedor_combo.get():
            proveedor_id = int(self.proveedor_combo.get().split(' - ')[0])
        
        if self.producto_id:
            exito, mensaje = self.producto_model.actualizar_producto(
                self.producto_id, codigo, nombre, descripcion, 
                categoria_id, precio, stock, proveedor_id
            )
        else:
            exito, mensaje = self.producto_model.crear_producto(
                codigo, nombre, descripcion, categoria_id, 
                precio, stock, proveedor_id
            )
        
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", mensaje)

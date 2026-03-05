import tkinter as tk
from tkinter import ttk, messagebox
from models.producto import Producto
from models.venta import Venta
from datetime import datetime
import os
import sys
from utils.moneda import formatear_moneda

class VentasView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.producto_model = Producto(db_manager)
        self.venta_model = Venta(db_manager)
        self.items_venta = []  # Lista de items en la venta actual
        self.productos_cache = {}  # Diccionario para guardar datos de productos buscados
        self.create_widgets()
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.producto_model = Producto(db_manager)
        self.venta_model = Venta(db_manager)
        
        self.items_venta = []  # Lista de items en la venta actual
        self.productos_cache = {}  # Diccionario para guardar datos de productos buscados
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets de la vista de ventas"""
        # Configurar fondo
        self.parent.configure(bg='white')
        
        # Título con color
        title_frame = tk.Frame(self.parent, bg='#2563EB', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="💰 NUEVA VENTA / FACTURA",
                font=("Arial", 18, "bold"),
                bg='#2563EB',
                fg='white').pack(expand=True)
        
        # Frame principal dividido en dos columnas
        main_container = tk.Frame(self.parent, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Columna izquierda - Agregar productos con scroll
        left_frame_wrapper = tk.Frame(main_container, bg='white', relief=tk.RIDGE, bd=1)
        left_frame_wrapper.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Canvas con scroll para frame izquierdo
        left_canvas = tk.Canvas(left_frame_wrapper, bg='white', highlightthickness=0)
        left_scrollbar = ttk.Scrollbar(left_frame_wrapper, orient=tk.VERTICAL, command=left_canvas.yview)
        left_frame = tk.Frame(left_canvas, bg='white')
        
        def on_left_frame_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        
        left_frame.bind("<Configure>", on_left_frame_configure)
        left_canvas.create_window((0, 0), window=left_frame, anchor="nw")
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        # Bind mousewheel para scroll izquierdo
        left_frame.bind("<MouseWheel>", lambda e: left_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        left_canvas.bind("<MouseWheel>", lambda e: left_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        left_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(left_frame, 
                text="Agregar Productos",
                font=("Arial", 13, "bold"),
                bg='white',
                fg='black').pack(pady=10)
        
        # Información del cliente
        client_frame = tk.Frame(left_frame, bg='white', relief=tk.RIDGE, bd=1)
        client_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(client_frame,
                text="Datos del Cliente",
                font=("Arial", 11, "bold"),
                bg='white',
                fg='black').grid(row=0, column=0, columnspan=4, pady=5)
        
        tk.Label(client_frame, 
                text="Nombre:",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black').grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.cliente_nombre_entry = tk.Entry(client_frame, width=30, font=("Arial", 10))
        self.cliente_nombre_entry.grid(row=1, column=1, pady=5, padx=5)
        
        tk.Label(client_frame,
            text="Documento:",
            font=("Arial", 10, "bold"),
            bg='white',
            fg='black').grid(row=1, column=2, sticky=tk.W, pady=5, padx=(10, 0))
        self.cliente_documento_entry = tk.Entry(client_frame, width=20, font=("Arial", 10))
        self.cliente_documento_entry.grid(row=1, column=3, pady=5, padx=5)

        # Método de pago
        tk.Label(client_frame, text="Método de Pago:", font=("Arial", 10, "bold"), bg='white', fg='black').grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.metodo_pago_var = tk.StringVar(value="Efectivo")
        self.metodo_pago_combo = ttk.Combobox(client_frame, textvariable=self.metodo_pago_var, state="readonly", font=("Arial", 10), width=18)
        self.metodo_pago_combo['values'] = ("Efectivo", "Transferencia", "Tarjeta")
        self.metodo_pago_combo.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)

        # Campo de recargo (solo visible si es Tarjeta)
        self.recargo_label = tk.Label(client_frame, text="Recargo %:", font=("Arial", 10, "bold"), bg='white', fg='black')
        self.recargo_entry = tk.Entry(client_frame, width=10, font=("Arial", 10))
        self.recargo_entry.insert(0, "0")
        self.recargo_label.grid_forget()
        self.recargo_entry.grid_forget()

        def on_metodo_pago_change(event=None):
            if self.metodo_pago_var.get() == "Tarjeta":
                self.recargo_label.grid(row=2, column=2, sticky=tk.W, pady=5, padx=(10, 0))
                self.recargo_entry.grid(row=2, column=3, pady=5, padx=5)
            else:
                self.recargo_label.grid_forget()
                self.recargo_entry.grid_forget()

        self.metodo_pago_combo.bind("<<ComboboxSelected>>", on_metodo_pago_change)
        
        # Buscar producto
        search_frame = tk.Frame(left_frame, bg='white', relief=tk.RIDGE, bd=1)
        search_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        tk.Label(search_frame,
                text="Buscar Producto",
                font=("Arial", 11, "bold"),
                bg='white',
                fg='black').grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W, padx=5)
        
        tk.Label(search_frame,
                text="Código o Nombre:",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black').grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10))
        self.search_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.EW)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        self.search_entry.bind('<Down>', self.on_search_arrow_down)
        self.search_entry.bind('<Up>', self.on_search_arrow_up)
        self.search_entry.bind('<Return>', self.on_search_enter)
        self.search_entry.bind('<KP_Enter>', self.on_search_enter)
        
        # Lista de productos
        self.productos_listbox = tk.Listbox(
            search_frame,
            height=8,
            font=("Arial", 9),
            selectbackground='#2563EB',
            selectforeground='white',
            exportselection=False,
            activestyle='none'
        )
        self.productos_listbox.grid(row=2, column=0, columnspan=2, pady=5, padx=5, sticky=tk.NSEW)
        self.productos_listbox.bind('<<ListboxSelect>>', self.on_producto_selected)
        self.productos_listbox.bind('<Return>', self.on_search_enter)
        self.productos_listbox.bind('<KP_Enter>', self.on_search_enter)
        
        scrollbar = ttk.Scrollbar(search_frame, orient=tk.VERTICAL, command=self.productos_listbox.yview)
        scrollbar.grid(row=2, column=2, sticky='ns', pady=5)
        self.productos_listbox.config(yscrollcommand=scrollbar.set)
        
        # Configurar peso de filas y columnas
        search_frame.grid_rowconfigure(2, weight=1)
        search_frame.grid_columnconfigure(1, weight=1)
        
        # Detalles del producto seleccionado
        detail_frame = tk.Frame(left_frame, bg='white', relief=tk.RIDGE, bd=1)
        detail_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(detail_frame,
                text="Detalles del Producto",
                font=("Arial", 11, "bold"),
                bg='white',
                fg='black').grid(row=0, column=0, columnspan=2, pady=5, padx=5)
        
        tk.Label(detail_frame,
                text="Producto:",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black').grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        self.producto_label = tk.Label(detail_frame, text="-", font=("Arial", 10, "bold"), bg='white', fg='black')
        self.producto_label.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)
        
        tk.Label(detail_frame,
                text="Precio:",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black').grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.precio_label = tk.Label(detail_frame, text="-", bg='white', fg='black')
        self.precio_label.grid(row=2, column=1, sticky=tk.W, pady=5, padx=5)
        
        tk.Label(detail_frame,
                text="Stock:",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black').grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        self.stock_label = tk.Label(detail_frame, text="-", bg='white', fg='black')
        self.stock_label.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)
        
        tk.Label(detail_frame,
                text="Cantidad:",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black').grid(row=4, column=0, sticky=tk.W, pady=5, padx=5)
        self.cantidad_entry = tk.Entry(detail_frame, width=10, font=("Arial", 10))
        self.cantidad_entry.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        self.cantidad_entry.insert(0, "1")
        
        tk.Label(detail_frame,
                text="Descuento %:",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black').grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        self.descuento_entry = tk.Entry(detail_frame, width=10, font=("Arial", 10))
        self.descuento_entry.grid(row=5, column=1, sticky=tk.W, pady=5, padx=5)
        self.descuento_entry.insert(0, "0")
        
        add_btn = tk.Button(detail_frame,
                           text="Agregar a la Venta",
                           font=('Arial', 10, 'bold'),
                           bg='#10B981',
                           fg='white',
                           activebackground='#059669',
                           bd=0,
                           pady=8,
                           cursor='hand2',
                           command=self.agregar_item)
        add_btn.grid(row=6, column=0, columnspan=2, pady=10, padx=5, sticky=tk.EW)
        
        # Columna derecha - Detalle de venta con scroll
        right_frame_wrapper = tk.Frame(main_container, bg='white')
        right_frame_wrapper.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Canvas con scroll para el frame derecho
        right_canvas = tk.Canvas(right_frame_wrapper, bg='white', highlightthickness=0)
        right_scrollbar = ttk.Scrollbar(right_frame_wrapper, orient=tk.VERTICAL, command=right_canvas.yview)
        right_frame = tk.Frame(right_canvas, bg='white')
        
        def on_right_frame_configure(event):
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))
        
        right_frame.bind("<Configure>", on_right_frame_configure)
        right_canvas.create_window((0, 0), window=right_frame, anchor="nw")
        right_canvas.configure(yscrollcommand=right_scrollbar.set)
        
        # Bind mousewheel para scroll derecho
        right_frame.bind("<MouseWheel>", lambda e: right_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        right_canvas.bind("<MouseWheel>", lambda e: right_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        right_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Etiqueta de detalle
        tk.Label(right_frame, text="Detalle de la Venta", font=("Arial", 11, "bold"), bg='white', fg='black').pack(fill=tk.X, pady=5, padx=10)
        
        # Tabla de items
        columns = ('producto', 'cantidad', 'precio', 'descuento', 'recargo', 'subtotal')
        self.items_tree = ttk.Treeview(right_frame, columns=columns, show='headings', height=15)

        self.items_tree.heading('producto', text='Producto')
        self.items_tree.heading('cantidad', text='Cantidad')
        self.items_tree.heading('precio', text='Precio Unit.')
        self.items_tree.heading('descuento', text='Desc. %')
        self.items_tree.heading('recargo', text='Recargo')
        self.items_tree.heading('subtotal', text='Subtotal')

        self.items_tree.column('producto', width=200)
        self.items_tree.column('cantidad', width=80, anchor=tk.CENTER)
        self.items_tree.column('precio', width=100, anchor=tk.E)
        self.items_tree.column('descuento', width=80, anchor=tk.CENTER)
        self.items_tree.column('recargo', width=80, anchor=tk.CENTER)
        self.items_tree.column('subtotal', width=100, anchor=tk.E)
        
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para la tabla
        tree_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.items_tree.config(yscrollcommand=tree_scrollbar.set)
        
        # Botón para eliminar item
        ttk.Button(right_frame, text="Eliminar Item Seleccionado", 
                  command=self.eliminar_item).pack(pady=5)
        
        # Totales con color
        totals_frame = tk.Frame(right_frame, bg='#F9FAFB', relief=tk.RIDGE, bd=2)
        totals_frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(totals_frame, text="Subtotal:", 
            font=("Arial", 11, "bold"),
            bg='#F9FAFB',
            fg='#374151').grid(row=0, column=0, sticky=tk.E, padx=10, pady=5)
        self.subtotal_label = tk.Label(totals_frame, text=formatear_moneda(0), 
                          font=("Arial", 11),
                          bg='#F9FAFB',
                          fg='#1F2937')
        self.subtotal_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)

        tk.Label(totals_frame, text="Descuento:", 
            font=("Arial", 11, "bold"),
            bg='#F9FAFB',
            fg='#374151').grid(row=1, column=0, sticky=tk.E, padx=10, pady=5)
        self.descuento_total_label = tk.Label(totals_frame, text=formatear_moneda(0), 
                     font=("Arial", 11),
                     bg='#F9FAFB',
                     fg='#DC2626')
        self.descuento_total_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)

        # Recargo
        tk.Label(totals_frame, text="Recargo:", font=("Arial", 11, "bold"), bg='#F9FAFB', fg='#374151').grid(row=2, column=0, sticky=tk.E, padx=10, pady=5)
        self.recargo_total_label = tk.Label(totals_frame, text=formatear_moneda(0), font=("Arial", 11), bg='#F9FAFB', fg='#F59E0B')
        self.recargo_total_label.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)

        # Separador (ahora debajo del recargo)
        tk.Frame(totals_frame, height=2, bg='#E5E7EB').grid(row=3, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

        tk.Label(totals_frame, text="TOTAL:", 
            font=("Arial", 16, "bold"),
            bg='#F9FAFB',
            fg='#1F2937').grid(row=4, column=0, sticky=tk.E, padx=10, pady=8)
        self.total_label = tk.Label(totals_frame, text=formatear_moneda(0), 
                       font=("Arial", 16, "bold"),
                       bg='#F9FAFB',
                       fg='#10B981')
        self.total_label.grid(row=4, column=1, sticky=tk.W, padx=10, pady=8)
        
        # Botones de acción con colores
        buttons_frame = tk.Frame(right_frame, bg='white')
        buttons_frame.pack(fill=tk.X, pady=10, padx=10)
        
        process_btn = tk.Button(buttons_frame,
                               text="✅ Procesar Venta",
                               font=('Arial', 11, 'bold'),
                               bg='#10B981',
                               fg='white',
                               activebackground='#059669',
                               activeforeground='white',
                               bd=0,
                               pady=12,
                               cursor='hand2',
                               command=self.procesar_venta)
        process_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        cancel_btn = tk.Button(buttons_frame,
                              text="❌ Cancelar / Nueva Venta",
                              font=('Arial', 11, 'bold'),
                              bg='#EF4444',
                              fg='white',
                              activebackground='#DC2626',
                              activeforeground='white',
                              bd=0,
                              pady=12,
                              cursor='hand2',
                              command=self.limpiar_venta)
        cancel_btn.pack(side=tk.RIGHT, padx=5, expand=True, fill=tk.X)
        
        self.producto_seleccionado = None
    
    def on_search_change(self, event):
        """Buscar productos mientras se escribe"""
        if event and event.keysym in ("Up", "Down"):
            return

        termino = self.search_entry.get().strip()
        
        self.productos_listbox.delete(0, tk.END)
        self.productos_cache = {}
        
        if len(termino) >= 2:
            productos = self.producto_model.buscar_producto(termino)
            for idx, prod in enumerate(productos):
                display_text = f"{prod[1]} - {prod[2]} (Stock: {prod[6]}) - {formatear_moneda(prod[5])}"
                self.productos_listbox.insert(tk.END, display_text)
                # Guardar datos del producto en el diccionario
                self.productos_cache[idx] = prod

    def _mover_seleccion_producto(self, paso):
        """Mover selección en la lista de productos con teclado"""
        total_items = self.productos_listbox.size()
        if total_items == 0:
            return "break"

        seleccion = self.productos_listbox.curselection()
        if seleccion:
            nuevo_indice = max(0, min(total_items - 1, seleccion[0] + paso))
        else:
            nuevo_indice = 0 if paso >= 0 else total_items - 1

        self.productos_listbox.selection_clear(0, tk.END)
        self.productos_listbox.selection_set(nuevo_indice)
        self.productos_listbox.activate(nuevo_indice)
        self.productos_listbox.see(nuevo_indice)
        self.on_producto_selected(None)
        return "break"

    def on_search_arrow_down(self, event):
        """Navegar resultados hacia abajo desde el buscador"""
        return self._mover_seleccion_producto(1)

    def on_search_arrow_up(self, event):
        """Navegar resultados hacia arriba desde el buscador"""
        return self._mover_seleccion_producto(-1)

    def on_search_enter(self, event):
        """Confirmar producto seleccionado y pasar a cantidad"""
        total_items = self.productos_listbox.size()
        if total_items == 0:
            return "break"

        seleccion = self.productos_listbox.curselection()
        if not seleccion:
            self.productos_listbox.selection_set(0)
            self.productos_listbox.activate(0)
            self.productos_listbox.see(0)
            self.on_producto_selected(None)

        self.cantidad_entry.focus()
        self.cantidad_entry.select_range(0, tk.END)
        return "break"
    
    def on_producto_selected(self, event):
        """Cuando se selecciona un producto de la lista"""
        selection = self.productos_listbox.curselection()
        if selection:
            index = selection[0]
            # Obtener datos del producto desde el caché
            if index in self.productos_cache:
                prod = self.productos_cache[index]
                self.producto_seleccionado = prod
                
                self.producto_label.config(text=prod[2])
                self.precio_label.config(text=formatear_moneda(prod[5]))
                self.stock_label.config(text=str(prod[6]))
    
    def agregar_item(self):
        """Agregar producto a la venta"""
        if not self.producto_seleccionado:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        try:
            cantidad = int(self.cantidad_entry.get())
            descuento = float(self.descuento_entry.get())
            
            if cantidad <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor a 0")
                return
            
            if cantidad > self.producto_seleccionado[6]:
                messagebox.showerror("Error", f"Stock insuficiente. Disponible: {self.producto_seleccionado[6]}")
                return
            
            if descuento < 0 or descuento > 100:
                messagebox.showerror("Error", "El descuento debe estar entre 0 y 100")
                return
            
            # Calcular subtotal
            precio = self.producto_seleccionado[5]
            subtotal_sin_desc = cantidad * precio
            descuento_monto = subtotal_sin_desc * (descuento / 100)
            subtotal = subtotal_sin_desc - descuento_monto
            
            # Agregar item a la lista
            # Recargo global (solo para mostrar en la columna, no por producto)
            metodo_pago = self.metodo_pago_var.get() if hasattr(self, 'metodo_pago_var') else "Efectivo"
            recargo_val = 0.0
            if metodo_pago == "Tarjeta":
                try:
                    recargo_val = float(self.recargo_entry.get())
                except Exception:
                    recargo_val = 0.0
            item = {
                'producto_id': self.producto_seleccionado[0],
                'producto_nombre': self.producto_seleccionado[2],
                'cantidad': cantidad,
                'precio_unitario': precio,
                'descuento_porcentaje': descuento,
                'recargo': recargo_val,
                'subtotal': subtotal
            }

            self.items_venta.append(item)

            # Agregar a la tabla
            self.items_tree.insert('', tk.END, values=(
                item['producto_nombre'],
                item['cantidad'],
                formatear_moneda(item['precio_unitario']),
                f"{item['descuento_porcentaje']}%",
                f"{item['recargo']}%",
                formatear_moneda(item['subtotal'])
            ))
            
            # Actualizar totales
            self.actualizar_totales()
            
            # Limpiar selección
            self.limpiar_seleccion()
            
        except ValueError:
            messagebox.showerror("Error", "Cantidad o descuento inválido")
    
    def eliminar_item(self):
        """Eliminar item seleccionado de la venta"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un item para eliminar")
            return
        
        # Obtener índice
        item_id = selection[0]
        index = self.items_tree.index(item_id)
        
        # Eliminar de la lista y tabla
        del self.items_venta[index]
        self.items_tree.delete(item_id)
        
        # Actualizar totales
        self.actualizar_totales()
    
    def actualizar_totales(self):
        """Actualizar los totales de la venta"""
        subtotal = sum(item['cantidad'] * item['precio_unitario'] for item in self.items_venta)
        descuento_total = sum(item['cantidad'] * item['precio_unitario'] * (item['descuento_porcentaje'] / 100) 
                             for item in self.items_venta)
        total = subtotal - descuento_total

        # Calcular recargo solo si corresponde
        recargo = 0.0
        metodo = self.metodo_pago_var.get() if hasattr(self, 'metodo_pago_var') else "Efectivo"
        if metodo == "Tarjeta":
            try:
                recargo_pct = float(self.recargo_entry.get())
                if recargo_pct > 0:
                    recargo = (total * recargo_pct) / 100
            except Exception:
                recargo = 0.0
        else:
            recargo = 0.0

        self.subtotal_label.config(text=formatear_moneda(subtotal))
        self.descuento_total_label.config(text=formatear_moneda(descuento_total))
        self.recargo_total_label.config(text=formatear_moneda(recargo))
        self.total_label.config(text=formatear_moneda(total + recargo))
    
    def limpiar_seleccion(self):
        """Limpiar la selección de producto"""
        self.search_entry.delete(0, tk.END)
        self.productos_listbox.delete(0, tk.END)
        self.producto_seleccionado = None
        self.producto_label.config(text="-")
        self.precio_label.config(text="-")
        self.stock_label.config(text="-")
        self.cantidad_entry.delete(0, tk.END)
        self.cantidad_entry.insert(0, "1")
        self.descuento_entry.delete(0, tk.END)
        self.descuento_entry.insert(0, "0")
        self.search_entry.focus()
    
    def limpiar_venta(self, omitir_confirmacion=False):
        """Limpiar toda la venta"""
        if self.items_venta and not omitir_confirmacion and not messagebox.askyesno("Confirmar", "¿Desea cancelar la venta actual?"):
            return
        
        self.items_venta = []
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        self.cliente_nombre_entry.delete(0, tk.END)
        self.cliente_documento_entry.delete(0, tk.END)
        if hasattr(self, 'metodo_pago_var'):
            self.metodo_pago_var.set("Efectivo")
        if hasattr(self, 'recargo_entry'):
            self.recargo_entry.delete(0, tk.END)
            self.recargo_entry.insert(0, "0")
            self.recargo_entry.grid_forget()
        if hasattr(self, 'recargo_label'):
            self.recargo_label.grid_forget()
        self.actualizar_totales()
        self.limpiar_seleccion()
    
    def procesar_venta(self):
        """Procesar y guardar la venta"""
        if not self.items_venta:
            messagebox.showwarning("Advertencia", "Agregue al menos un producto a la venta")
            return
        
        cliente_nombre = self.cliente_nombre_entry.get().strip()
        cliente_documento = self.cliente_documento_entry.get().strip()
        
        if not cliente_nombre:
            if not messagebox.askyesno("Confirmar", "¿Desea continuar sin nombre de cliente?"):
                return
            cliente_nombre = "Cliente Genérico"
        
        # Crear venta
        # Obtener método de pago y recargo
        metodo_pago = self.metodo_pago_var.get() if hasattr(self, 'metodo_pago_var') else "Efectivo"
        try:
            recargo_val = float(self.recargo_entry.get()) if metodo_pago == "Tarjeta" else 0.0
        except Exception:
            recargo_val = 0.0

        exito, mensaje, venta_id = self.venta_model.crear_venta(
            self.user_data['id'],
            cliente_nombre,
            cliente_documento,
            self.items_venta,
            metodo_pago,
            recargo_val
        )
        
        if exito:
            messagebox.showinfo("Éxito", f"Venta procesada exitosamente\nFactura: {mensaje}")
            
            # Preguntar si desea imprimir factura
            if messagebox.askyesno("Factura", "¿Desea generar la factura en PDF?"):
                self.generar_factura_pdf(venta_id)
            
            # Limpiar venta
            self.limpiar_venta(omitir_confirmacion=True)
        else:
            messagebox.showerror("Error", mensaje)
    
    def generar_factura_pdf(self, venta_id):
        """Generar factura en PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import inch
            
            # Obtener datos de la venta
            venta_data = self.venta_model.obtener_venta_por_id(venta_id)
            
            if not venta_data:
                messagebox.showerror("Error", "No se pudo obtener la información de la venta")
                return
            
            # Crear directorio de facturas si no existe
            if getattr(sys, 'frozen', False):
                facturas_dir = os.path.join(os.path.dirname(sys.executable), 'reports')
            else:
                facturas_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'reports')
            
            os.makedirs(facturas_dir, exist_ok=True)
            
            # Nombre del archivo
            venta = venta_data['venta']
            filename = os.path.join(facturas_dir, f"{venta[1]}.pdf")
            
            # Crear PDF
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Título
            c.setFont("Helvetica-Bold", 20)
            c.drawString(1*inch, height - 1*inch, "FACTURA DE VENTA")
            
            # Información de la factura
            c.setFont("Helvetica", 12)
            y = height - 1.5*inch
            c.drawString(1*inch, y, f"Factura N°: {venta[1]}")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"Fecha: {venta[7]}")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"Vendedor: {venta[8]}")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"Método de Pago: {venta[9]}")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"Recargo: {venta[10]}%")
            
            # Información del cliente
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1*inch, y, "Cliente:")
            c.setFont("Helvetica", 12)
            y -= 0.3*inch
            c.drawString(1*inch, y, f"Nombre: {venta[2] or 'N/A'}")
            y -= 0.3*inch
            c.drawString(1*inch, y, f"Documento: {venta[3] or 'N/A'}")
            
            # Tabla de productos
            y -= 0.5*inch
            c.setFont("Helvetica-Bold", 10)
            c.drawString(1*inch, y, "Producto")
            c.drawString(3.5*inch, y, "Cant.")
            c.drawString(4.2*inch, y, "Precio")
            c.drawString(5*inch, y, "Desc.")
            c.drawString(5.8*inch, y, "Subtotal")
            
            y -= 0.05*inch
            c.line(1*inch, y, 7*inch, y)
            
            y -= 0.25*inch
            c.setFont("Helvetica", 10)
            
            for detalle in venta_data['detalles']:
                c.drawString(1*inch, y, detalle[5][:30])  # Producto
                c.drawString(3.5*inch, y, str(detalle[0]))  # Cantidad
                c.drawString(4.2*inch, y, formatear_moneda(detalle[1]))  # Precio
                c.drawString(5*inch, y, f"{detalle[2]:.0f}%")  # Descuento
                c.drawString(5.8*inch, y, formatear_moneda(detalle[4]))  # Subtotal
                y -= 0.25*inch
            
            # Totales
            y -= 0.3*inch
            c.line(1*inch, y, 7*inch, y)
            
            y -= 0.3*inch
            c.setFont("Helvetica-Bold", 12)
            c.drawString(4.5*inch, y, f"Subtotal:")
            c.drawString(5.8*inch, y, formatear_moneda(venta[4]))

            y -= 0.3*inch
            c.drawString(4.5*inch, y, f"Descuento:")
            c.drawString(5.8*inch, y, formatear_moneda(venta[5]))

            # Mostrar recargo y total con recargo
            y -= 0.3*inch
            c.drawString(4.5*inch, y, f"Recargo:")
            # Calcular el monto del recargo
            recargo_monto = (venta[6] * venta[10]) / 100 if venta[10] else 0.0
            c.drawString(5.8*inch, y, formatear_moneda(recargo_monto))

            y -= 0.4*inch
            c.setFont("Helvetica-Bold", 14)
            c.drawString(4.5*inch, y, f"TOTAL:")
            total_con_recargo = venta[6] + recargo_monto
            c.drawString(5.8*inch, y, formatear_moneda(total_con_recargo))
            
            c.save()
            
            messagebox.showinfo("Éxito", f"Factura generada:\n{filename}")
            
            # Abrir el PDF
            os.startfile(filename)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar factura: {str(e)}")

import sys

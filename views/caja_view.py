import tkinter as tk
from tkinter import ttk, messagebox
from models.caja import Caja
from datetime import datetime
from utils.moneda import formatear_moneda, formatear_moneda_con_signo, parsear_monto

class CajaView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.caja_model = Caja(db_manager)
        
        self.create_widgets()
        self.actualizar_estado_caja()
    
    def create_widgets(self):
        """Crear widgets"""
        self.parent.configure(bg='#F0F4F8')
        
        # Título con color (más compacto)
        title_frame = tk.Frame(self.parent, bg='#8B5CF6', height=45)
        title_frame.pack(fill=tk.X, pady=(0, 5))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="💰 GESTIÓN DE CAJA",
                font=("Arial", 14, "bold"),
                bg='#8B5CF6',
                fg='white').pack(expand=True)
        
        # Frame principal con scroll
        main_container = tk.Frame(self.parent, bg='#F0F4F8')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Canvas con scrollbar
        canvas = tk.Canvas(main_container, bg='#F0F4F8', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#F0F4F8')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width() or 1)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Actualizar ancho del canvas cuando cambia tamaño
        def on_canvas_configure(event):
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Frame de estado de caja (compacto)
        self.estado_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.RIDGE, bd=1)
        self.estado_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=3)
        
        # Título del estado
        tk.Label(self.estado_frame, text="Estado de la Caja", font=("Arial", 10, "bold"),
                bg='white', fg='black').pack(pady=3)
        
        # Estado actual
        self.estado_label = tk.Label(self.estado_frame, text="Caja Cerrada", 
                                     font=("Arial", 9, "bold"), bg='white', fg='red')
        self.estado_label.pack(pady=1)
        
        # Info de caja abierta (compacto)
        self.info_frame = tk.Frame(self.estado_frame, bg='white')
        self.info_frame.pack(pady=3, fill=tk.X)
        
        # Botones de acción (más compactos)
        buttons_frame = tk.Frame(scrollable_frame, bg='#F0F4F8')
        buttons_frame.pack(pady=3, fill=tk.X, padx=5)
        
        # Frame interno para centrar botones
        buttons_inner = tk.Frame(buttons_frame, bg='#F0F4F8')
        buttons_inner.pack()
        
        self.btn_abrir = tk.Button(buttons_inner, text="🔓 Abrir", font=('Arial', 9, 'bold'),
                                   bg='#10B981', fg='white', width=14, height=1,
                                   command=self.abrir_caja)
        self.btn_abrir.pack(side=tk.LEFT, padx=3)
        
        self.btn_cerrar = tk.Button(buttons_inner, text="🔒 Cerrar", font=('Arial', 9, 'bold'),
                                    bg='#EF4444', fg='white', width=14, height=1,
                                    command=self.cerrar_caja, state=tk.DISABLED)
        self.btn_cerrar.pack(side=tk.LEFT, padx=3)
        
        tk.Button(buttons_inner, text="📊 Historial", font=('Arial', 9),
                 bg='#3B82F6', fg='white', width=14, height=1,
                 command=self.ver_historial).pack(side=tk.LEFT, padx=3)
        
        # Botón eliminar solo para admin
        if self.user_data['rol'] == 'admin':
            tk.Button(buttons_inner, text="🗑️ Eliminar", font=('Arial', 9),
                     bg='#DC2626', fg='white', width=14, height=1,
                     command=self.eliminar_caja).pack(side=tk.LEFT, padx=3)
        
        # Frame para agregar movimientos (compacto)
        tk.Label(scrollable_frame, text="Agregar Movimiento", font=("Arial", 9, "bold"),
                bg='#F0F4F8', fg='black').pack(pady=(8, 2), anchor=tk.W, padx=5)
        
        self.movimientos_frame = tk.Frame(scrollable_frame, bg='white', relief=tk.RIDGE, bd=1)
        self.movimientos_frame.pack(fill=tk.X, padx=5, pady=2)
        
        movimientos_btn_frame = tk.Frame(self.movimientos_frame, bg='white', padx=3, pady=3)
        movimientos_btn_frame.pack()
        
        self.btn_agregar_efectivo = tk.Button(movimientos_btn_frame, text="💵 Efectivo", 
                                              font=('Arial', 9, 'bold'), bg='#10B981', fg='white',
                                              width=15, height=1, command=self.agregar_movimiento_efectivo,
                                              state=tk.DISABLED)
        self.btn_agregar_efectivo.pack(side=tk.LEFT, padx=3)
        
        self.btn_agregar_transferencia = tk.Button(movimientos_btn_frame, text="🏦 Transfer.", 
                                                   font=('Arial', 9, 'bold'), bg='#3B82F6', fg='white',
                                                   width=15, height=1, command=self.agregar_movimiento_transferencia,
                                                   state=tk.DISABLED)
        self.btn_agregar_transferencia.pack(side=tk.LEFT, padx=3)
        
        self.btn_agregar_tarjeta = tk.Button(movimientos_btn_frame, text="💳 Tarjeta", 
                                             font=('Arial', 9, 'bold'), bg='#8B5CF6', fg='white',
                                             width=15, height=1, command=self.agregar_movimiento_tarjeta,
                                             state=tk.DISABLED)
        self.btn_agregar_tarjeta.pack(side=tk.LEFT, padx=3)
        
        # Tabla de movimientos (compacta)
        tk.Label(scrollable_frame, text="Movimientos de Caja", font=("Arial", 9, "bold"),
                bg='#F0F4F8', fg='black').pack(pady=(8, 2), anchor=tk.W, padx=5)
        
        mov_columns = ('id', 'tipo', 'categoria', 'monto', 'descripcion', 'fecha')
        self.tree_movimientos = ttk.Treeview(scrollable_frame, columns=mov_columns, show='headings', height=5)
        
        self.tree_movimientos.heading('id', text='ID')
        self.tree_movimientos.heading('tipo', text='Tipo')
        self.tree_movimientos.heading('categoria', text='Categoría/Origen')
        self.tree_movimientos.heading('monto', text='Monto')
        self.tree_movimientos.heading('descripcion', text='Descripción')
        self.tree_movimientos.heading('fecha', text='Fecha')
        
        self.tree_movimientos.column('id', width=30)
        self.tree_movimientos.column('tipo', width=70)
        self.tree_movimientos.column('categoria', width=120)
        self.tree_movimientos.column('monto', width=75, anchor=tk.E)
        self.tree_movimientos.column('descripcion', width=140)
        self.tree_movimientos.column('fecha', width=90)
        
        self.tree_movimientos.pack(fill=tk.BOTH, expand=False, padx=5, pady=2)
        
        # Bind click derecho para eliminar
        self.tree_movimientos.bind('<Button-3>', self.menu_eliminar_movimiento)
        
        # Tabla de historial reciente (compacta)
        tk.Label(scrollable_frame, text="Historial Reciente", font=("Arial", 9, "bold"),
                bg='#F0F4F8', fg='black').pack(pady=(8, 2), anchor=tk.W, padx=5)
        
        columns = ('id', 'usuario', 'fecha_apertura', 'fecha_cierre', 'monto_inicial', 'monto_final', 'estado')
        self.tree = ttk.Treeview(scrollable_frame, columns=columns, show='headings', height=6)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('usuario', text='Usuario')
        self.tree.heading('fecha_apertura', text='Apertura')
        self.tree.heading('fecha_cierre', text='Cierre')
        self.tree.heading('monto_inicial', text='Monto Inicial')
        self.tree.heading('monto_final', text='Monto Final')
        self.tree.heading('estado', text='Estado')
        
        self.tree.column('id', width=35)
        self.tree.column('usuario', width=90)
        self.tree.column('fecha_apertura', width=95)
        self.tree.column('fecha_cierre', width=95)
        self.tree.column('monto_inicial', width=80, anchor=tk.E)
        self.tree.column('monto_final', width=80, anchor=tk.E)
        self.tree.column('estado', width=60)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Bind doble click para ver detalles
        self.tree.bind('<Double-Button-1>', lambda e: self.ver_detalle_caja())
        
        # Scrollbars del canvas
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar historial
        self.cargar_historial()
    
    def actualizar_estado_caja(self):
        """Actualizar el estado de la caja en la interfaz"""
        caja_abierta = self.caja_model.obtener_caja_abierta()
        
        # Limpiar info anterior
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        if caja_abierta:
            self.estado_label.config(text="✅ Caja Abierta", fg='#10B981')
            self.btn_abrir.config(state=tk.DISABLED)
            self.btn_cerrar.config(state=tk.NORMAL)
            self.btn_agregar_efectivo.config(state=tk.NORMAL)
            self.btn_agregar_transferencia.config(state=tk.NORMAL)
            self.btn_agregar_tarjeta.config(state=tk.NORMAL)
            
            # Mostrar información
            tk.Label(self.info_frame, text=f"Abierta por: {caja_abierta['usuario']}", 
                    bg='white', fg='black', font=("Arial", 10)).pack(anchor=tk.W, padx=20)
            tk.Label(self.info_frame, text=f"Fecha: {caja_abierta['fecha_apertura'][:16]}", 
                    bg='white', fg='black', font=("Arial", 10)).pack(anchor=tk.W, padx=20)
            tk.Label(self.info_frame, text=f"Monto Inicial: {formatear_moneda(caja_abierta['monto_inicial'])}", 
                    bg='white', fg='black', font=("Arial", 10, 'bold')).pack(anchor=tk.W, padx=20)
            
            # Cargar movimientos
            self.cargar_movimientos(caja_abierta['id'])
        else:
            self.estado_label.config(text="❌ Caja Cerrada", fg='#EF4444')
            self.btn_abrir.config(state=tk.NORMAL)
            self.btn_cerrar.config(state=tk.DISABLED)
            self.btn_agregar_efectivo.config(state=tk.DISABLED)
            self.btn_agregar_transferencia.config(state=tk.DISABLED)
            self.btn_agregar_tarjeta.config(state=tk.DISABLED)
            
            tk.Label(self.info_frame, text="No hay caja abierta actualmente", 
                    bg='white', fg='gray', font=("Arial", 10, 'italic')).pack(pady=10)
            
            # Limpiar movimientos
            for item in self.tree_movimientos.get_children():
                self.tree_movimientos.delete(item)
    
    def abrir_caja(self):
        """Abrir diálogo para abrir caja"""
        AbrirCajaDialog(self.parent, self.db_manager, self.user_data, self.actualizar_todo)
    
    def cerrar_caja(self):
        """Abrir diálogo para cerrar caja"""
        caja_abierta = self.caja_model.obtener_caja_abierta()
        if caja_abierta:
            CerrarCajaDialog(self.parent, self.db_manager, caja_abierta, self.actualizar_todo)
        else:
            messagebox.showwarning("Advertencia", "No hay caja abierta")
    
    def ver_historial(self):
        """Ver historial completo de cajas"""
        HistorialCajasDialog(self.parent, self.db_manager)
    
    def eliminar_caja(self):
        """Eliminar la caja seleccionada (solo admin)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una caja del historial para eliminar")
            return
        
        item = self.tree.item(selection[0])
        caja_id = item['values'][0]
        estado = item['values'][6]
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", 
                              f"¿Está seguro que desea eliminar la caja #{caja_id}?\n\n"
                              "Esta acción no se puede deshacer."):
            success, mensaje = self.caja_model.eliminar_caja(caja_id)
            
            if success:
                messagebox.showinfo("Éxito", mensaje)
                self.actualizar_todo()
            else:
                messagebox.showerror("Error", mensaje)
    
    def ver_detalle_caja(self):
        """Ver detalle de la caja seleccionada"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        caja_id = item['values'][0]
        
        caja = self.caja_model.obtener_caja_por_id(caja_id)
        if caja:
            DetalleCajaDialog(self.parent, caja, self.db_manager)
    
    def cargar_historial(self):
        """Cargar historial reciente en la tabla"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cajas = self.caja_model.obtener_cajas(limit=10)
        for caja in cajas:
            self.tree.insert('', tk.END, values=(
                caja['id'],
                caja['usuario'],
                caja['fecha_apertura'][:16] if caja['fecha_apertura'] else '',
                caja['fecha_cierre'][:16] if caja['fecha_cierre'] else 'Abierta',
                formatear_moneda(caja['monto_inicial']),
                formatear_moneda(caja['monto_final']) if caja['monto_final'] is not None else 'N/A',
                caja['estado'].capitalize()
            ))
    
    def actualizar_todo(self):
        """Actualizar toda la vista"""
        self.actualizar_estado_caja()
        self.cargar_historial()
    
    def cargar_movimientos(self, caja_id):
        """Cargar movimientos de la caja abierta"""
        for item in self.tree_movimientos.get_children():
            self.tree_movimientos.delete(item)
        
        movimientos = self.caja_model.obtener_movimientos(caja_id)
        for mov in movimientos:
            self.tree_movimientos.insert('', tk.END, values=(
                mov['id'],
                mov['tipo'].upper(),
                mov.get('categoria') or '',
                formatear_moneda(mov['monto']),
                mov['descripcion'] or '',
                mov['fecha'][:16]
            ))
    
    def agregar_movimiento_efectivo(self):
        """Agregar movimiento de efectivo"""
        caja = self.caja_model.obtener_caja_abierta()
        if caja:
            AgregarMovimientoDialog(self.parent, self.db_manager, caja['id'], 'efectivo', self.actualizar_estado_caja)
    
    def agregar_movimiento_transferencia(self):
        """Agregar movimiento de transferencia"""
        caja = self.caja_model.obtener_caja_abierta()
        if caja:
            AgregarMovimientoDialog(self.parent, self.db_manager, caja['id'], 'transferencia', self.actualizar_estado_caja)
    
    def agregar_movimiento_tarjeta(self):
        """Agregar movimiento de tarjeta"""
        caja = self.caja_model.obtener_caja_abierta()
        if caja:
            AgregarMovimientoDialog(self.parent, self.db_manager, caja['id'], 'tarjeta', self.actualizar_estado_caja)
    
    def menu_eliminar_movimiento(self, event):
        """Menú para eliminar movimiento"""
        selection = self.tree_movimientos.selection()
        if not selection:
            return
        
        # Crear menú contextual
        menu = tk.Menu(self.parent, tearoff=0)
        menu.add_command(label="Eliminar", command=lambda: self.eliminar_movimiento(selection[0]))
        menu.post(event.x_root, event.y_root)
    
    def eliminar_movimiento(self, item):
        """Eliminar un movimiento"""
        valores = self.tree_movimientos.item(item, 'values')
        mov_id = valores[0]
        
        if messagebox.askyesno("Confirmar", "¿Eliminar este movimiento?"):
            success, msg = self.caja_model.eliminar_movimiento(mov_id)
            if success:
                messagebox.showinfo("Éxito", msg)
                self.actualizar_estado_caja()
            else:
                messagebox.showerror("Error", msg)


class AbrirCajaDialog:
    def __init__(self, parent, db_manager, user_data, callback):
        self.db_manager = db_manager
        self.user_data = user_data
        self.callback = callback
        self.caja_model = Caja(db_manager)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Abrir Caja")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar
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
        
        tk.Label(main_frame, text="🔓 Abrir Caja", font=("Arial", 14, "bold"),
                bg='white', fg='#10B981').pack(pady=10)
        
        # Usuario
        tk.Label(main_frame, text=f"Usuario: {self.user_data['nombre_completo']}", 
                bg='white', fg='black', font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        
        # Monto inicial
        tk.Label(main_frame, text="Monto Inicial:", bg='white', fg='black',
                font=("Arial", 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.monto_entry = tk.Entry(main_frame, width=30, font=("Arial", 11))
        self.monto_entry.pack(anchor=tk.W, pady=5)
        self.monto_entry.focus()
        
        # Observaciones
        tk.Label(main_frame, text="Observaciones (opcional):", bg='white', fg='black',
                font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        self.obs_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self.obs_entry.pack(anchor=tk.W, pady=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=10)
        
        tk.Button(buttons_frame, text="Abrir Caja", font=('Arial', 10), bg='#10B981', fg='white',
                 width=12, command=self.abrir).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=('Arial', 10), bg='#EF4444', fg='white',
                 width=12, command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def abrir(self):
        """Abrir la caja"""
        try:
            monto = parsear_monto(self.monto_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El monto inicial debe ser un número válido")
            return
        
        if monto < 0:
            messagebox.showerror("Error", "El monto inicial no puede ser negativo")
            return
        
        observaciones = self.obs_entry.get().strip()
        
        success, mensaje = self.caja_model.abrir_caja(self.user_data['id'], monto, observaciones)
        
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", mensaje)


class AgregarMovimientoDialog:
    def __init__(self, parent, db_manager, caja_id, tipo, callback):
        self.db_manager = db_manager
        self.caja_model = Caja(db_manager)
        self.caja_id = caja_id
        self.tipo = tipo
        self.callback = callback
        
        tipo_titles = {
            'efectivo': '💵 Agregar Efectivo',
            'transferencia': '🏦 Agregar Transferencia',
            'tarjeta': '💳 Agregar Tarjeta'
        }
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(tipo_titles.get(tipo, 'Agregar Movimiento'))
        self.dialog.geometry("500x460")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 200
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tipo_labels = {
            'efectivo': ('💵 Agregar Efectivo', '#10B981'),
            'transferencia': ('🏦 Agregar Transferencia', '#3B82F6'),
            'tarjeta': ('💳 Agregar Tarjeta', '#8B5CF6')
        }
        
        titulo, color = tipo_labels.get(self.tipo, ('Agregar Movimiento', '#6B7280'))
        tk.Label(main_frame, text=titulo, font=("Arial", 14, "bold"),
                bg='white', fg=color).pack(pady=10)
        
        # Tipo de transacción (ingreso o egreso)
        tk.Label(main_frame, text="Tipo:", font=("Arial", 11, "bold"), bg='white').pack(anchor=tk.W, pady=10)
        
        self.tipo_var = tk.StringVar(value="ingreso")
        ingreso_frame = tk.Frame(main_frame, bg='white')
        ingreso_frame.pack(anchor=tk.W, pady=5)
        tk.Radiobutton(ingreso_frame, text="Ingreso (+)", variable=self.tipo_var, value="ingreso",
                      font=("Arial", 10), bg='white', fg='#10B981').pack(side=tk.LEFT)
        
        if self.tipo in ('efectivo', 'transferencia'):
            tk.Radiobutton(ingreso_frame, text="Retiro (-)", variable=self.tipo_var, value="retiro",
                          font=("Arial", 10), bg='white', fg='#EF4444').pack(side=tk.LEFT, padx=20)

        # Categoria de ingreso
        self.categoria_ingreso_frame = tk.Frame(main_frame, bg='white')
        self.categoria_ingreso_frame.pack(anchor=tk.W, fill=tk.X, pady=(10, 0))
        tk.Label(self.categoria_ingreso_frame, text="Origen del ingreso:", font=("Arial", 11, "bold"), bg='white').pack(anchor=tk.W, pady=(0, 5))
        self.categoria_ingreso_var = tk.StringVar(value="Reparación")
        self.categoria_ingreso_combo = ttk.Combobox(
            self.categoria_ingreso_frame,
            textvariable=self.categoria_ingreso_var,
            values=["Reparación", "Ventas en general", "Venta celulares"],
            state="readonly",
            width=24
        )
        self.categoria_ingreso_combo.pack(anchor=tk.W, pady=5)

        # Categoria de egreso
        self.categoria_egreso_frame = tk.Frame(main_frame, bg='white')
        self.categoria_egreso_frame.pack(anchor=tk.W, fill=tk.X, pady=(10, 0))
        tk.Label(self.categoria_egreso_frame, text="Categoría de egreso:", font=("Arial", 11, "bold"), bg='white').pack(anchor=tk.W, pady=(0, 5))
        self.categoria_egreso_var = tk.StringVar(value="Otros")
        self.categoria_egreso_combo = ttk.Combobox(
            self.categoria_egreso_frame,
            textvariable=self.categoria_egreso_var,
            values=["Pago técnico", "Publicidad", "Impuestos", "Empleados", "Otros"],
            state="readonly",
            width=24
        )
        self.categoria_egreso_combo.pack(anchor=tk.W, pady=5)
        
        # Monto
        tk.Label(main_frame, text="Monto ($):", font=("Arial", 11, "bold"), bg='white').pack(anchor=tk.W, pady=(10, 5))
        self.monto_entry = tk.Entry(main_frame, width=40, font=("Arial", 11))
        self.monto_entry.pack(anchor=tk.W, pady=5)
        self.monto_entry.focus()
        
        # Descripción (solo para retiros de efectivo)
        self.desc_frame = tk.Frame(main_frame, bg='white')
        self.desc_frame.pack(anchor=tk.W, fill=tk.X, pady=5)
        
        self.desc_label = tk.Label(self.desc_frame, text="Descripción (para retiros):", 
                                   font=("Arial", 10), bg='white')
        self.desc_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.desc_entry = tk.Entry(self.desc_frame, width=40, font=("Arial", 10))
        self.desc_entry.pack(anchor=tk.W, pady=5)
        
        # Ajustar visibilidad inicial
        self.actualizar_descripcion()
        
        # Bind para mostrar/ocultar descripción
        self.tipo_var.trace('w', self.actualizar_descripcion)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=20)
        
        tk.Button(buttons_frame, text="✅ Agregar", font=('Arial', 10, 'bold'), 
                 bg='#10B981', fg='white', width=12, command=self.agregar).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="❌ Cancelar", font=('Arial', 10, 'bold'), 
                 bg='#EF4444', fg='white', width=12, command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def actualizar_descripcion(self, *args):
        """Mostrar/ocultar descripción según tipo"""
        if self.tipo in ('efectivo', 'transferencia') and self.tipo_var.get() == 'retiro':
            self.categoria_ingreso_frame.pack_forget()
            self.categoria_egreso_frame.pack(anchor=tk.W, fill=tk.X, pady=(10, 0))
            self.desc_frame.pack(anchor=tk.W, fill=tk.X, pady=5)
        else:
            self.categoria_egreso_frame.pack_forget()
            self.desc_frame.pack_forget()
            self.categoria_ingreso_frame.pack(anchor=tk.W, fill=tk.X, pady=(10, 0))
    
    def agregar(self):
        """Agregar movimiento"""
        try:
            monto = parsear_monto(self.monto_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido")
            return
        
        if monto <= 0:
            messagebox.showerror("Error", "El monto debe ser mayor a 0")
            return
        
        # Si es retiro, negar el monto
        if self.tipo_var.get() == 'retiro':
            monto = -monto
            categoria = self.categoria_egreso_var.get().strip() or 'Otros'
            detalle = self.desc_entry.get().strip()
            descripcion = categoria if not detalle else f"{categoria}: {detalle}"
        else:
            categoria_ingreso = self.categoria_ingreso_var.get().strip() or 'Reparación'
            descripcion = f"Ingreso: {categoria_ingreso}"
            categoria = categoria_ingreso
        
        success, msg = self.caja_model.agregar_movimiento(self.caja_id, self.tipo, monto, descripcion, categoria)
        
        if success:
            messagebox.showinfo("Éxito", msg)
            self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", msg)

class HistorialCajasDialog:
    def __init__(self, parent, db_manager, user_data, callback):
        self.db_manager = db_manager
        self.user_data = user_data
        self.callback = callback
        self.caja_model = Caja(db_manager)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Abrir Caja")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar
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
        
        tk.Label(main_frame, text="🔓 Abrir Caja", font=("Arial", 14, "bold"),
                bg='white', fg='#10B981').pack(pady=10)
        
        # Usuario
        tk.Label(main_frame, text=f"Usuario: {self.user_data['nombre_completo']}", 
                bg='white', fg='black', font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        
        # Monto inicial
        tk.Label(main_frame, text="Monto Inicial:", bg='white', fg='black',
                font=("Arial", 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.monto_entry = tk.Entry(main_frame, width=30, font=("Arial", 11))
        self.monto_entry.pack(anchor=tk.W, pady=5)
        self.monto_entry.focus()
        
        # Observaciones
        tk.Label(main_frame, text="Observaciones (opcional):", bg='white', fg='black',
                font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        self.obs_entry = tk.Entry(main_frame, width=30, font=("Arial", 10))
        self.obs_entry.pack(anchor=tk.W, pady=5)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=10)
        
        tk.Button(buttons_frame, text="Abrir Caja", font=('Arial', 10), bg='#10B981', fg='white',
                 width=12, command=self.abrir).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=('Arial', 10), bg='#EF4444', fg='white',
                 width=12, command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def abrir(self):
        """Abrir la caja"""
        try:
            monto = parsear_monto(self.monto_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "El monto inicial debe ser un número válido")
            return
        
        if monto < 0:
            messagebox.showerror("Error", "El monto inicial no puede ser negativo")
            return
        
        observaciones = self.obs_entry.get().strip()
        
        success, mensaje = self.caja_model.abrir_caja(self.user_data['id'], monto, observaciones)
        
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", mensaje)


class CerrarCajaDialog:
    def __init__(self, parent, db_manager, caja_data, callback):
        self.db_manager = db_manager
        self.caja_data = caja_data
        self.callback = callback
        self.caja_model = Caja(db_manager)
        
        # Obtener movimientos para calcular total
        self.movimientos = self.caja_model.obtener_movimientos(self.caja_data['id'])
        self.total_movimientos = sum(mov['monto'] for mov in self.movimientos)
        self.monto_final_calculado = self.caja_data['monto_inicial'] + self.total_movimientos
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cerrar Caja")
        self.dialog.geometry("550x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 275
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 275
        self.dialog.geometry(f"550x550+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="🔒 Cerrar Caja", font=("Arial", 14, "bold"),
                bg='white', fg='#EF4444').pack(pady=10)
        
        # Info de apertura
        info_frame = tk.Frame(main_frame, bg='#F3F4F6', relief=tk.RIDGE, bd=1)
        info_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(info_frame, text=f"Monto Inicial: {formatear_moneda(self.caja_data['monto_inicial'])}", 
                bg='#F3F4F6', fg='black', font=("Arial", 10, 'bold')).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(info_frame, text=f"Abierta: {self.caja_data['fecha_apertura'][:16]}", 
                bg='#F3F4F6', fg='black', font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=2)
        
        # Separador
        tk.Frame(info_frame, bg='#E5E7EB', height=1).pack(fill=tk.X, pady=8)
        
        # Resumen de movimientos
        tk.Label(info_frame, text="Resumen de Movimientos:", font=("Arial", 10, "bold"),
                bg='#F3F4F6', fg='black').pack(anchor=tk.W, padx=10, pady=(5, 3))
        
        if self.movimientos:
            # Tabla con movimientos
            mov_frame = tk.Frame(info_frame, bg='white')
            mov_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Headers
            header_frame = tk.Frame(mov_frame, bg='#E5E7EB')
            header_frame.pack(fill=tk.X)
            tk.Label(header_frame, text="Tipo", font=("Arial", 8, "bold"), bg='#E5E7EB', width=12).pack(side=tk.LEFT, padx=2, pady=2)
            tk.Label(header_frame, text="Monto", font=("Arial", 8, "bold"), bg='#E5E7EB', width=12, justify=tk.RIGHT).pack(side=tk.LEFT, padx=2, pady=2)
            
            # Movimientos
            for mov in self.movimientos:
                row_frame = tk.Frame(mov_frame, bg='white')
                row_frame.pack(fill=tk.X)
                
                color_monto = '#10B981' if mov['monto'] >= 0 else '#EF4444'
                tk.Label(row_frame, text=mov['tipo'].capitalize(), font=("Arial", 8), bg='white', width=12).pack(side=tk.LEFT, padx=2, pady=1)
                tk.Label(row_frame, text=formatear_moneda_con_signo(mov['monto']), font=("Arial", 8), bg='white', fg=color_monto, width=12, justify=tk.RIGHT).pack(side=tk.LEFT, padx=2, pady=1)
        else:
            tk.Label(info_frame, text="Sin movimientos registrados", font=("Arial", 9, "italic"),
                    bg='#F3F4F6', fg='#6B7280').pack(anchor=tk.W, padx=10, pady=3)
        
        # Separador
        tk.Frame(info_frame, bg='#E5E7EB', height=1).pack(fill=tk.X, pady=8)
        
        # Totales
        tk.Label(info_frame, text=f"Total Movimientos: {formatear_moneda_con_signo(self.total_movimientos)}", 
                bg='#F3F4F6', fg='#8B5CF6' if self.total_movimientos >= 0 else '#EF4444', 
                font=("Arial", 10, 'bold')).pack(anchor=tk.W, padx=10, pady=2)
        tk.Label(info_frame, text=f"Monto Final: {formatear_moneda(self.monto_final_calculado)}", 
                bg='#F3F4F6', fg='#10B981', font=("Arial", 11, 'bold')).pack(anchor=tk.W, padx=10, pady=5)
        
        # Observaciones
        obs_frame = tk.Frame(main_frame, bg='white')
        obs_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(obs_frame, text="Observaciones (opcional):", font=("Arial", 9),
                bg='white', fg='black').pack(anchor=tk.W, pady=3)
        self.obs_entry = tk.Entry(obs_frame, width=50, font=("Arial", 10))
        self.obs_entry.pack(anchor=tk.W, pady=3, fill=tk.X)
        
        # Botones
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=15)
        
        tk.Button(buttons_frame, text="✅ Cerrar Caja", font=('Arial', 10, 'bold'), bg='#10B981', fg='white',
                 width=12, command=self.cerrar).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="❌ Cancelar", font=('Arial', 10, 'bold'), bg='#EF4444', fg='white',
                 width=12, command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def cerrar(self):
        """Cerrar la caja"""
        observaciones = self.obs_entry.get().strip()
        
        success, mensaje = self.caja_model.cerrar_caja(
            self.caja_data['id'], self.monto_final_calculado, 0, 0, 0, 0, 0, 0, observaciones
        )
        
        if success:
            messagebox.showinfo("Éxito", f"Caja cerrada correctamente\n\nMonto Final: {formatear_moneda(self.monto_final_calculado)}")
            self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", mensaje)


class DetalleCajaDialog:
    def __init__(self, parent, caja_data, db_manager):
        self.caja_data = caja_data
        self.db_manager = db_manager
        self.caja_model = Caja(db_manager)
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Detalle de Caja")
        self.dialog.geometry("600x700")
        self.dialog.transient(parent)
        
        # Centrar
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 300
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 350
        self.dialog.geometry(f"600x700+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        estado_color = '#10B981' if self.caja_data['estado'] == 'abierta' else '#6B7280'
        tk.Label(main_frame, text=f"Caja #{self.caja_data['id']}", font=("Arial", 16, "bold"),
                bg='white', fg=estado_color).pack(pady=10)
        
        # Frame de información
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Datos básicos
        datos = [
            ("Usuario:", self.caja_data['usuario']),
            ("Estado:", self.caja_data['estado'].capitalize()),
            ("Fecha Apertura:", self.caja_data['fecha_apertura'][:16] if self.caja_data['fecha_apertura'] else 'N/A'),
            ("Fecha Cierre:", self.caja_data['fecha_cierre'][:16] if self.caja_data['fecha_cierre'] else 'No cerrada'),
            ("", ""),
            ("Monto Inicial:", formatear_moneda(self.caja_data['monto_inicial'])),
        ]
        
        for label, value in datos:
            if label == "":
                tk.Frame(info_frame, bg='#E5E7EB', height=1).pack(fill=tk.X, pady=5)
            else:
                row_frame = tk.Frame(info_frame, bg='white')
                row_frame.pack(fill=tk.X, pady=3)
                tk.Label(row_frame, text=label, bg='white', fg='black', 
                        font=("Arial", 10, 'bold'), width=20, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(row_frame, text=value, bg='white', fg='black',
                        font=("Arial", 10), anchor=tk.W).pack(side=tk.LEFT)
        
        # Movimientos
        tk.Label(info_frame, text="Movimientos:", bg='white', fg='black',
                font=("Arial", 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
        
        movimientos = self.caja_model.obtener_movimientos(self.caja_data['id'])
        
        if movimientos:
            for mov in movimientos:
                tipo = mov.get('tipo', '')
                monto = mov.get('monto', 0)
                categoria = mov.get('categoria', '') or ''
                descripcion = mov.get('descripcion', '')
                
                # Formatear tipo
                iconos = {'efectivo': '💵', 'transferencia': '🏦', 'tarjeta': '💳'}
                icono = iconos.get(tipo, '💰')
                
                # Color según monto
                color = '#EF4444' if monto < 0 else '#10B981'
                signo = '-' if monto < 0 else '+'
                
                row_frame = tk.Frame(info_frame, bg='white')
                row_frame.pack(fill=tk.X, pady=2)
                
                # Tipo y monto
                monto_text = f"{signo}{formatear_moneda(abs(monto))}"
                texto_mov = f"{icono} {tipo.capitalize()}"
                
                tk.Label(row_frame, text=texto_mov, bg='white', fg='black',
                        font=("Arial", 9), width=15, anchor=tk.W).pack(side=tk.LEFT)
                tk.Label(row_frame, text=monto_text, bg='white', fg=color,
                        font=("Arial", 9, 'bold'), anchor=tk.W).pack(side=tk.LEFT, padx=(10, 0))

                if categoria:
                    tk.Label(row_frame, text=f"[{categoria}]", bg='white', fg='#374151',
                        font=("Arial", 8, 'italic')).pack(side=tk.LEFT, padx=(8, 0))
                
                # Mostrar descripción si existe (para retiros)
                if descripcion:
                    desc_frame = tk.Frame(info_frame, bg='white')
                    desc_frame.pack(fill=tk.X, pady=(0, 5), padx=(20, 0))
                    tk.Label(desc_frame, text=f"└─ {descripcion}", bg='white', fg='#6B7280',
                            font=("Arial", 8, 'italic')).pack(anchor=tk.W)
        else:
            tk.Label(info_frame, text="Sin movimientos", bg='white', fg='#9CA3AF',
                    font=("Arial", 9)).pack(anchor=tk.W, pady=5)
        
        # Separador
        tk.Frame(info_frame, bg='#E5E7EB', height=2).pack(fill=tk.X, pady=10)
        
        # Monto final
        if self.caja_data['monto_final'] is not None:
            row_frame = tk.Frame(info_frame, bg='white')
            row_frame.pack(fill=tk.X, pady=5)
            tk.Label(row_frame, text="Monto Final:", bg='white', fg='black',
                    font=("Arial", 12, 'bold'), width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row_frame, text=formatear_moneda(self.caja_data['monto_final']), bg='white',
                    fg='#10B981', font=("Arial", 12, 'bold'), anchor=tk.W).pack(side=tk.LEFT)
            
            # Diferencia
            diferencia = self.caja_data['monto_final'] - self.caja_data['monto_inicial']
            color_dif = '#10B981' if diferencia >= 0 else '#EF4444'
            row_frame = tk.Frame(info_frame, bg='white')
            row_frame.pack(fill=tk.X, pady=5)
            tk.Label(row_frame, text="Diferencia:", bg='white', fg='black',
                    font=("Arial", 11, 'bold'), width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row_frame, text=formatear_moneda(diferencia), bg='white',
                    fg=color_dif, font=("Arial", 11, 'bold'), anchor=tk.W).pack(side=tk.LEFT)
        
        # Observaciones
        if self.caja_data.get('observaciones'):
            tk.Label(info_frame, text="Observaciones:", bg='white', fg='black',
                    font=("Arial", 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
            tk.Label(info_frame, text=self.caja_data['observaciones'], bg='white', fg='black',
                    font=("Arial", 9), wraplength=500, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Botón cerrar
        tk.Button(main_frame, text="Cerrar", font=('Arial', 10), bg='#6B7280', fg='white',
                 width=15, command=self.dialog.destroy).pack(pady=20)


class HistorialCajasDialog:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.caja_model = Caja(db_manager)
        self.buscar_var = tk.StringVar()
        self.filtro_categoria_var = tk.StringVar(value="Todas")
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Historial de Cajas")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        
        # Centrar
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 450
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
        self.dialog.geometry(f"900x600+{x}+{y}")
        
        self.create_widgets()
        self.cargar_historial()
    
    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        
        # Título
        title_frame = tk.Frame(self.dialog, bg='#8B5CF6', height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame, text="📊 Historial de Cajas", font=("Arial", 14, "bold"),
                bg='#8B5CF6', fg='white').pack(expand=True)
        
        # Filtros
        filter_frame = tk.Frame(self.dialog, bg='white')
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(filter_frame, text="Desde:", bg='white', fg='black').grid(row=0, column=0, padx=5)
        self.fecha_desde = tk.Entry(filter_frame, width=12)
        self.fecha_desde.grid(row=0, column=1, padx=5)
        
        tk.Label(filter_frame, text="Hasta:", bg='white', fg='black').grid(row=0, column=2, padx=5)
        self.fecha_hasta = tk.Entry(filter_frame, width=12)
        self.fecha_hasta.grid(row=0, column=3, padx=5)
        
        tk.Label(filter_frame, text="Buscar:", bg='white', fg='black').grid(row=0, column=4, padx=(12, 5))
        self.buscar_entry = tk.Entry(filter_frame, textvariable=self.buscar_var, width=20)
        self.buscar_entry.grid(row=0, column=5, padx=5)
        self.buscar_entry.bind('<KeyRelease>', self.on_busqueda_historial)

        tk.Label(filter_frame, text="Categoría:", bg='white', fg='black').grid(row=0, column=6, padx=(12, 5))
        self.categoria_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filtro_categoria_var,
            values=[
                "Todas",
                "Reparación",
                "Ventas en general",
                "Venta celulares",
                "Pago técnico",
                "Publicidad",
                "Impuestos",
                "Empleados",
                "Otros",
            ],
            state="readonly",
            width=18
        )
        self.categoria_combo.grid(row=0, column=7, padx=5)
        self.categoria_combo.bind('<<ComboboxSelected>>', lambda _e: self.cargar_historial())

        tk.Button(filter_frame, text="Filtrar", bg='#3B82F6', fg='white',
               command=self.cargar_historial).grid(row=0, column=8, padx=5)
        tk.Button(filter_frame, text="Limpiar", bg='#6B7280', fg='white',
               command=self.limpiar_filtros).grid(row=0, column=9, padx=5)
        
        # Tabla
        columns = ('id', 'usuario', 'apertura', 'cierre', 'inicial', 'final', 'diferencia', 'estado')
        self.tree = ttk.Treeview(self.dialog, columns=columns, show='headings', height=20)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('usuario', text='Usuario')
        self.tree.heading('apertura', text='Apertura')
        self.tree.heading('cierre', text='Cierre')
        self.tree.heading('inicial', text='Inicial')
        self.tree.heading('final', text='Final')
        self.tree.heading('diferencia', text='Diferencia')
        self.tree.heading('estado', text='Estado')
        
        self.tree.column('id', width=50)
        self.tree.column('usuario', width=120)
        self.tree.column('apertura', width=130)
        self.tree.column('cierre', width=130)
        self.tree.column('inicial', width=80, anchor=tk.E)
        self.tree.column('final', width=80, anchor=tk.E)
        self.tree.column('diferencia', width=80, anchor=tk.E)
        self.tree.column('estado', width=80)
        
        scrollbar = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5, side=tk.LEFT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble click
        self.tree.bind('<Double-Button-1>', lambda e: self.ver_detalle())
    
    def cargar_historial(self):
        """Cargar historial"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        fecha_desde = self.fecha_desde.get().strip() or None
        fecha_hasta = self.fecha_hasta.get().strip() or None
        termino = self.buscar_var.get().strip().lower()
        categoria = self.filtro_categoria_var.get().strip() or "Todas"
        
        cajas = self.caja_model.obtener_cajas(fecha_desde, fecha_hasta, limit=100)
        
        for caja in cajas:
            fecha_apertura = (caja.get('fecha_apertura') or '')[:16]
            fecha_cierre = (caja.get('fecha_cierre') or '')[:16]
            texto_busqueda = ' '.join([
                str(caja.get('id') or ''),
                str(caja.get('usuario') or ''),
                fecha_apertura,
                fecha_cierre,
                str(caja.get('estado') or '')
            ]).lower()
            if termino and termino not in texto_busqueda:
                continue
            if categoria != "Todas" and not self._caja_tiene_categoria(caja['id'], categoria):
                continue

            diferencia = ''
            if caja['monto_final'] is not None:
                dif = caja['monto_final'] - caja['monto_inicial']
                diferencia = formatear_moneda(dif)
            
            self.tree.insert('', tk.END, values=(
                caja['id'],
                caja['usuario'],
                caja['fecha_apertura'][:16] if caja['fecha_apertura'] else '',
                caja['fecha_cierre'][:16] if caja['fecha_cierre'] else 'Abierta',
                formatear_moneda(caja['monto_inicial']),
                formatear_moneda(caja['monto_final']) if caja['monto_final'] is not None else 'N/A',
                diferencia,
                caja['estado'].capitalize()
            ))
    
    def limpiar_filtros(self):
        """Limpiar filtros"""
        self.fecha_desde.delete(0, tk.END)
        self.fecha_hasta.delete(0, tk.END)
        self.buscar_var.set('')
        self.filtro_categoria_var.set('Todas')
        self.cargar_historial()

    def on_busqueda_historial(self, _event=None):
        """Actualizar historial al escribir en el buscador"""
        self.cargar_historial()

    def _caja_tiene_categoria(self, caja_id, categoria):
        """Verificar si una caja tiene al menos un movimiento de la categoría indicada."""
        movimientos = self.caja_model.obtener_movimientos(caja_id)
        categoria_lower = categoria.lower()
        for mov in movimientos:
            mov_categoria = (mov.get('categoria') or '').strip()
            mov_descripcion = (mov.get('descripcion') or '').strip()
            if mov_categoria.lower() == categoria_lower:
                return True
            if not mov_categoria and mov_descripcion.lower().startswith(categoria_lower.lower()):
                return True
            if categoria_lower in mov_descripcion.lower():
                return True
        return False
    
    def ver_detalle(self):
        """Ver detalle de caja seleccionada"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        caja_id = item['values'][0]
        
        caja = self.caja_model.obtener_caja_por_id(caja_id)
        if caja:
            DetalleCajaDialog(self.dialog, caja, self.db_manager)

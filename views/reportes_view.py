import tkinter as tk
from tkinter import ttk, messagebox
from models.venta import Venta
from datetime import datetime, timedelta

class ReportesView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.venta_model = Venta(db_manager)
        
        self.create_widgets()
        self.cargar_ventas()
    
    def create_widgets(self):
        """Crear widgets"""
        self.parent.configure(bg='#F0F4F8')
        
        # Título con color
        title_frame = tk.Frame(self.parent, bg='#F59E0B', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="📊 REPORTES DE VENTAS",
                font=("Arial", 18, "bold"),
                bg='#F59E0B',
                fg='white').pack(expand=True)
        
        # Frame de filtros
        filter_frame = tk.Frame(self.parent, bg='white')
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Etiqueta de filtros
        tk.Label(filter_frame, text="Filtros", font=("Arial", 11, "bold"), bg='white', fg='black').grid(row=0, column=0, columnspan=9, sticky=tk.W, padx=5, pady=5)
        
        # Fecha inicio
        tk.Label(filter_frame, text="Desde:", bg='white', fg='black').grid(row=1, column=0, padx=5, pady=5)
        self.fecha_inicio_entry = tk.Entry(filter_frame, width=15)
        self.fecha_inicio_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Fecha fin
        tk.Label(filter_frame, text="Hasta:", bg='white', fg='black').grid(row=1, column=2, padx=5, pady=5)
        self.fecha_fin_entry = tk.Entry(filter_frame, width=15)
        self.fecha_fin_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Botones de filtro rápido
        tk.Button(filter_frame, text="Hoy", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_hoy).grid(row=1, column=4, padx=5, pady=5)
        tk.Button(filter_frame, text="Esta Semana", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_semana).grid(row=1, column=5, padx=5, pady=5)
        tk.Button(filter_frame, text="Este Mes", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_mes).grid(row=1, column=6, padx=5, pady=5)
        tk.Button(filter_frame, text="Limpiar", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.limpiar_filtros).grid(row=1, column=7, padx=5, pady=5)
        
        # Aplicar filtros
        tk.Button(filter_frame, text="Aplicar", font=("Arial", 9), bg='#2563EB', fg='white', relief=tk.RAISED,
                  command=self.cargar_ventas).grid(row=1, column=8, padx=5, pady=5)
        
        # Estadísticas
        stats_frame = tk.Frame(self.parent, bg='white')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Etiqueta de estadísticas
        tk.Label(stats_frame, text="Estadísticas", font=("Arial", 11, "bold"), bg='white', fg='black').grid(row=0, column=0, columnspan=6, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(stats_frame, text="Total Ventas:", bg='white', fg='black').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.total_ventas_label = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), bg='white', fg='black')
        self.total_ventas_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        tk.Label(stats_frame, text="Total Ingresos:", bg='white', fg='black').grid(row=1, column=2, sticky=tk.W, padx=20)
        self.total_ingresos_label = tk.Label(stats_frame, text="$0.00", font=("Arial", 11, "bold"), bg='white', fg='#10B981')
        self.total_ingresos_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        tk.Label(stats_frame, text="Promedio por Venta:", bg='white', fg='black').grid(row=1, column=4, sticky=tk.W, padx=20)
        self.promedio_label = tk.Label(stats_frame, text="$0.00", font=("Arial", 11, "bold"), bg='white', fg='black')
        self.promedio_label.grid(row=1, column=5, sticky=tk.W, padx=5)
        
        # Tabla de ventas
        columns = ('id', 'factura', 'cliente', 'total', 'fecha', 'vendedor')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=15)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('factura', text='N° Factura')
        self.tree.heading('cliente', text='Cliente')
        self.tree.heading('total', text='Total')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('vendedor', text='Vendedor')
        
        self.tree.column('id', width=50)
        self.tree.column('factura', width=150)
        self.tree.column('cliente', width=200)
        self.tree.column('total', width=120, anchor=tk.E)
        self.tree.column('fecha', width=150)
        self.tree.column('vendedor', width=180)
        
        # Scrollbar vertical
        scrollbar_v = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar_v.set)
        
        # Scrollbar horizontal
        scrollbar_h = ttk.Scrollbar(self.parent, orient=tk.HORIZONTAL, command=self.tree.xview)
        scrollbar_h.pack(fill=tk.X)
        self.tree.config(xscrollcommand=scrollbar_h.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame de botones
        button_frame = tk.Frame(self.parent, bg='#F0F4F8')
        button_frame.pack(pady=10)
        
        # Botón ver detalles
        ttk.Button(button_frame, text="Ver Detalles de Venta", 
                  command=self.ver_detalles).pack(side=tk.LEFT, padx=5)
        
        # Botón eliminar venta (solo visible para admin)
        self.btn_eliminar = ttk.Button(button_frame, text="Eliminar Venta", 
                  command=self.eliminar_venta)
        self.btn_eliminar.pack(side=tk.LEFT, padx=5)
        
        # Mostrar/ocultar botón según rol del usuario
        if self.user_data['rol'] != 'admin':
            self.btn_eliminar.config(state=tk.DISABLED)
        
        # Formato de fecha
        ttk.Label(self.parent, text="Formato de fecha: YYYY-MM-DD (ej: 2026-01-15)", 
                 font=("Arial", 8), foreground="gray").pack()
    
    def filtrar_hoy(self):
        """Filtrar ventas de hoy"""
        hoy = datetime.now().strftime('%Y-%m-%d')
        self.fecha_inicio_entry.delete(0, tk.END)
        self.fecha_inicio_entry.insert(0, hoy)
        self.fecha_fin_entry.delete(0, tk.END)
        self.fecha_fin_entry.insert(0, hoy)
    
    def filtrar_semana(self):
        """Filtrar ventas de esta semana"""
        hoy = datetime.now()
        inicio_semana = (hoy - timedelta(days=hoy.weekday())).strftime('%Y-%m-%d')
        fin_semana = hoy.strftime('%Y-%m-%d')
        self.fecha_inicio_entry.delete(0, tk.END)
        self.fecha_inicio_entry.insert(0, inicio_semana)
        self.fecha_fin_entry.delete(0, tk.END)
        self.fecha_fin_entry.insert(0, fin_semana)
    
    def filtrar_mes(self):
        """Filtrar ventas de este mes"""
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1).strftime('%Y-%m-%d')
        fin_mes = hoy.strftime('%Y-%m-%d')
        self.fecha_inicio_entry.delete(0, tk.END)
        self.fecha_inicio_entry.insert(0, inicio_mes)
        self.fecha_fin_entry.delete(0, tk.END)
        self.fecha_fin_entry.insert(0, fin_mes)
    
    def limpiar_filtros(self):
        """Limpiar filtros"""
        self.fecha_inicio_entry.delete(0, tk.END)
        self.fecha_fin_entry.delete(0, tk.END)
    
    def cargar_ventas(self):
        """Cargar ventas con filtros"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener filtros
        fecha_inicio = self.fecha_inicio_entry.get().strip() or None
        fecha_fin = self.fecha_fin_entry.get().strip() or None
        
        # Cargar ventas
        ventas = self.venta_model.listar_ventas(fecha_inicio, fecha_fin)
        for venta in ventas:
            self.tree.insert('', tk.END, values=(
                venta[0], venta[1], venta[2] or '-', 
                f"${venta[3]:.2f}", venta[4], venta[5]
            ))
        
        # Actualizar estadísticas
        stats = self.venta_model.obtener_estadisticas(fecha_inicio, fecha_fin)
        if stats:
            self.total_ventas_label.config(text=str(stats[0]))
            self.total_ingresos_label.config(text=f"${stats[1]:.2f}")
            self.promedio_label.config(text=f"${stats[2]:.2f}")
    
    def ver_detalles(self):
        """Ver detalles de la venta seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una venta")
            return
        
        item = self.tree.item(selection[0])
        venta_id = item['values'][0]
        
        # Obtener detalles
        venta_data = self.venta_model.obtener_venta_por_id(venta_id)
        
        if not venta_data:
            messagebox.showerror("Error", "No se pudo cargar la venta")
            return
        
        # Crear ventana de detalles
        DetalleVentaDialog(self.parent, venta_data)
    
    def eliminar_venta(self):
        """Eliminar una venta seleccionada (solo para admin)"""
        # Verificar que es admin
        if self.user_data['rol'] != 'admin':
            messagebox.showerror("Acceso Denegado", "Solo los administradores pueden eliminar ventas")
            return
        
        # Verificar que haya seleccionado una venta
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una venta para eliminar")
            return
        
        item = self.tree.item(selection[0])
        venta_id = item['values'][0]
        numero_factura = item['values'][1]
        
        # Confirmar eliminación
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar la venta {numero_factura}?\n\n"
            f"Se devolverá el stock y se descontará del total de ingresos.",
            icon=messagebox.WARNING
        )
        
        if not respuesta:
            return
        
        # Eliminar venta
        success, message = self.venta_model.eliminar_venta(venta_id)
        
        if success:
            messagebox.showinfo("Éxito", message)
            # Recargar lista de ventas
            self.cargar_ventas()
        else:
            messagebox.showerror("Error", message)


class DetalleVentaDialog:
    def __init__(self, parent, venta_data):
        self.venta_data = venta_data
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Detalle de Venta")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 350
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 250
        self.dialog.geometry(f"700x500+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        venta = self.venta_data['venta']
        
        # Información de la venta
        info_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(info_frame, text="Información de la Venta", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Factura: {venta[1]}", font=("Arial", 12, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Fecha: {venta[7]}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Vendedor: {venta[8]}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Cliente: {venta[2] or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Documento: {venta[3] or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        
        # Detalles
        tk.Label(main_frame, text="Detalle de Productos:", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W, pady=(10, 5))
        
        columns = ('producto', 'cantidad', 'precio', 'descuento', 'subtotal')
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=10)
        
        tree.heading('producto', text='Producto')
        tree.heading('cantidad', text='Cantidad')
        tree.heading('precio', text='Precio Unit.')
        tree.heading('descuento', text='Descuento')
        tree.heading('subtotal', text='Subtotal')
        
        tree.column('producto', width=250)
        tree.column('cantidad', width=80, anchor=tk.CENTER)
        tree.column('precio', width=100, anchor=tk.E)
        tree.column('descuento', width=100, anchor=tk.E)
        tree.column('subtotal', width=100, anchor=tk.E)
        
        for detalle in self.venta_data['detalles']:
            tree.insert('', tk.END, values=(
                detalle[5],  # Producto
                detalle[0],  # Cantidad
                f"${detalle[1]:.2f}",  # Precio
                f"{detalle[2]:.0f}% (${detalle[3]:.2f})",  # Descuento
                f"${detalle[4]:.2f}"  # Subtotal
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Totales
        totals_frame = ttk.Frame(main_frame)
        totals_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(totals_frame, text="Subtotal:", 
                 font=("Arial", 11, "bold")).grid(row=0, column=0, sticky=tk.E, padx=5)
        ttk.Label(totals_frame, text=f"${venta[4]:.2f}", 
                 font=("Arial", 11)).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(totals_frame, text="Descuento:", 
                 font=("Arial", 11, "bold")).grid(row=1, column=0, sticky=tk.E, padx=5)
        ttk.Label(totals_frame, text=f"${venta[5]:.2f}", 
                 font=("Arial", 11)).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(totals_frame, text="TOTAL:", 
                 font=("Arial", 13, "bold")).grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        ttk.Label(totals_frame, text=f"${venta[6]:.2f}", 
                 font=("Arial", 13, "bold"), foreground="green").grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Botón cerrar
        ttk.Button(main_frame, text="Cerrar", 
                  command=self.dialog.destroy).pack(pady=10)

import tkinter as tk
from tkinter import ttk, messagebox
from models.venta import Venta
from models.reparacion import Reparacion
from datetime import datetime, timedelta

class ReportesView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.venta_model = Venta(db_manager)
        self.reparacion_model = Reparacion(db_manager)
        
        self.create_widgets()
        self.cargar_ventas()
    
    def create_widgets(self):
        """Crear widgets con pestañas"""
        self.parent.configure(bg='#F0F4F8')
        
        # Título con color
        title_frame = tk.Frame(self.parent, bg='#F59E0B', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="📊 REPORTES",
                font=("Arial", 18, "bold"),
                bg='#F59E0B',
                fg='white').pack(expand=True)
        
        # Crear pestañas
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Pestaña de Ventas
        ventas_frame = ttk.Frame(notebook)
        notebook.add(ventas_frame, text="💰 Ventas")
        self.crear_tab_ventas(ventas_frame)
        
        # Pestaña de Reparaciones
        reparaciones_frame = ttk.Frame(notebook)
        notebook.add(reparaciones_frame, text="🔧 Reparaciones")
        self.crear_tab_reparaciones(reparaciones_frame)
        
        # Cargar reparaciones automáticamente
        self.cargar_reparaciones()
    
    def crear_tab_ventas(self, parent):
        """Crear la pestaña de ventas"""
        # Frame de filtros
        filter_frame = tk.Frame(parent, bg='white')
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
        stats_frame = tk.Frame(parent, bg='white')
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
        self.tree_ventas = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        self.tree_ventas.heading('id', text='ID')
        self.tree_ventas.heading('factura', text='N° Factura')
        self.tree_ventas.heading('cliente', text='Cliente')
        self.tree_ventas.heading('total', text='Total')
        self.tree_ventas.heading('fecha', text='Fecha')
        self.tree_ventas.heading('vendedor', text='Vendedor')
        
        self.tree_ventas.column('id', width=50)
        self.tree_ventas.column('factura', width=150)
        self.tree_ventas.column('cliente', width=200)
        self.tree_ventas.column('total', width=120, anchor=tk.E)
        self.tree_ventas.column('fecha', width=150)
        self.tree_ventas.column('vendedor', width=180)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree_ventas.yview)
        scrollbar_h = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree_ventas.xview)
        self.tree_ventas.config(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree_ventas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(fill=tk.X)
        
        # Frame de botones
        button_frame = tk.Frame(parent, bg='#F0F4F8')
        button_frame.pack(pady=10)
        
        # Botón ver detalles
        ttk.Button(button_frame, text="Ver Detalles de Venta", 
                  command=self.ver_detalles_venta).pack(side=tk.LEFT, padx=5)
        
        # Botón eliminar venta
        ttk.Button(button_frame, text="Eliminar Venta", 
                  command=self.eliminar_venta).pack(side=tk.LEFT, padx=5)
        
        # Formato de fecha
        ttk.Label(parent, text="Formato de fecha: YYYY-MM-DD (ej: 2026-01-15)", 
                 font=("Arial", 8), foreground="gray").pack()
    
    def crear_tab_reparaciones(self, parent):
        """Crear la pestaña de reparaciones"""
        # Frame de filtros
        filter_frame = tk.Frame(parent, bg='white')
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Etiqueta de filtros
        tk.Label(filter_frame, text="Filtros", font=("Arial", 11, "bold"), bg='white', fg='black').grid(row=0, column=0, columnspan=10, sticky=tk.W, padx=5, pady=5)
        
        # Fecha inicio
        tk.Label(filter_frame, text="Desde:", bg='white', fg='black').grid(row=1, column=0, padx=5, pady=5)
        self.fecha_inicio_rep_entry = tk.Entry(filter_frame, width=15)
        self.fecha_inicio_rep_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Fecha fin
        tk.Label(filter_frame, text="Hasta:", bg='white', fg='black').grid(row=1, column=2, padx=5, pady=5)
        self.fecha_fin_rep_entry = tk.Entry(filter_frame, width=15)
        self.fecha_fin_rep_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Filtro por estado
        tk.Label(filter_frame, text="Estado:", bg='white', fg='black').grid(row=1, column=4, padx=5, pady=5)
        self.estado_rep_var = tk.StringVar(value="todos")
        estado_combo = ttk.Combobox(filter_frame, textvariable=self.estado_rep_var, width=12,
                                   values=['todos', 'pendiente', 'en_proceso', 'completada', 'cancelada'],
                                   state='readonly')
        estado_combo.grid(row=1, column=5, padx=5, pady=5)
        
        # Botones de filtro rápido
        tk.Button(filter_frame, text="Hoy", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_hoy_rep).grid(row=1, column=6, padx=5, pady=5)
        tk.Button(filter_frame, text="Este Mes", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_mes_rep).grid(row=1, column=7, padx=5, pady=5)
        tk.Button(filter_frame, text="Limpiar", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.limpiar_filtros_rep).grid(row=1, column=8, padx=5, pady=5)
        
        # Aplicar filtros
        tk.Button(filter_frame, text="Aplicar", font=("Arial", 9), bg='#2563EB', fg='white', relief=tk.RAISED,
                  command=self.cargar_reparaciones).grid(row=1, column=9, padx=5, pady=5)
        
        # Estadísticas
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Etiqueta de estadísticas
        tk.Label(stats_frame, text="Estadísticas", font=("Arial", 11, "bold"), bg='white', fg='black').grid(row=0, column=0, columnspan=8, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(stats_frame, text="Total Reparaciones:", bg='white', fg='black').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.total_reparaciones_label = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), bg='white', fg='black')
        self.total_reparaciones_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        tk.Label(stats_frame, text="Total Ingresos:", bg='white', fg='black').grid(row=1, column=2, sticky=tk.W, padx=20)
        self.total_ingresos_rep_label = tk.Label(stats_frame, text="$0.00", font=("Arial", 11, "bold"), bg='white', fg='#10B981')
        self.total_ingresos_rep_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        tk.Label(stats_frame, text="Total Seña:", bg='white', fg='black').grid(row=1, column=4, sticky=tk.W, padx=20)
        self.total_sena_label = tk.Label(stats_frame, text="$0.00", font=("Arial", 11, "bold"), bg='white', fg='#F59E0B')
        self.total_sena_label.grid(row=1, column=5, sticky=tk.W, padx=5)
        
        tk.Label(stats_frame, text="Promedio por Reparación:", bg='white', fg='black').grid(row=1, column=6, sticky=tk.W, padx=20)
        self.promedio_rep_label = tk.Label(stats_frame, text="$0.00", font=("Arial", 11, "bold"), bg='white', fg='black')
        self.promedio_rep_label.grid(row=1, column=7, sticky=tk.W, padx=5)
        
        # Tabla de reparaciones
        columns = ('numero', 'cliente', 'dispositivo', 'estado', 'sena', 'total', 'fecha')
        self.tree_reparaciones = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        self.tree_reparaciones.heading('numero', text='N° Orden')
        self.tree_reparaciones.heading('cliente', text='Cliente')
        self.tree_reparaciones.heading('dispositivo', text='Dispositivo')
        self.tree_reparaciones.heading('estado', text='Estado')
        self.tree_reparaciones.heading('sena', text='Seña')
        self.tree_reparaciones.heading('total', text='Total')
        self.tree_reparaciones.heading('fecha', text='Fecha')
        
        self.tree_reparaciones.column('numero', width=120)
        self.tree_reparaciones.column('cliente', width=180)
        self.tree_reparaciones.column('dispositivo', width=120)
        self.tree_reparaciones.column('estado', width=100)
        self.tree_reparaciones.column('sena', width=100, anchor=tk.E)
        self.tree_reparaciones.column('total', width=100, anchor=tk.E)
        self.tree_reparaciones.column('fecha', width=130)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree_reparaciones.yview)
        scrollbar_h = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree_reparaciones.xview)
        self.tree_reparaciones.config(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree_reparaciones.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(fill=tk.X)
        
        # Frame de botones
        button_frame = tk.Frame(parent, bg='#F0F4F8')
        button_frame.pack(pady=10)
        
        # Botón ver detalles
        ttk.Button(button_frame, text="Ver Detalles de Reparación", 
                  command=self.ver_detalles_reparacion).pack(side=tk.LEFT, padx=5)
        
        # Formato de fecha
        ttk.Label(parent, text="Formato de fecha: YYYY-MM-DD (ej: 2026-01-15)", 
                 font=("Arial", 8), foreground="gray").pack()
    
    # ============= MÉTODOS PARA VENTAS =============
    
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
        for item in self.tree_ventas.get_children():
            self.tree_ventas.delete(item)
        
        # Obtener filtros
        fecha_inicio = self.fecha_inicio_entry.get().strip() or None
        fecha_fin = self.fecha_fin_entry.get().strip() or None
        
        # Cargar ventas
        ventas = self.venta_model.listar_ventas(fecha_inicio, fecha_fin)
        for venta in ventas:
            self.tree_ventas.insert('', tk.END, values=(
                venta[0], venta[1], venta[2] or '-', 
                f"${venta[3]:.2f}", venta[4], venta[5]
            ))
        
        # Actualizar estadísticas
        stats = self.venta_model.obtener_estadisticas(fecha_inicio, fecha_fin)
        if stats:
            self.total_ventas_label.config(text=str(stats[0]))
            self.total_ingresos_label.config(text=f"${stats[1]:.2f}")
            self.promedio_label.config(text=f"${stats[2]:.2f}")
    
    def ver_detalles_venta(self):
        """Ver detalles de la venta seleccionada"""
        selection = self.tree_ventas.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una venta")
            return
        
        item = self.tree_ventas.item(selection[0])
        venta_id = item['values'][0]
        
        # Obtener detalles
        venta_data = self.venta_model.obtener_venta_por_id(venta_id)
        
        if not venta_data:
            messagebox.showerror("Error", "No se pudo cargar la venta")
            return
        
        # Crear ventana de detalles
        DetalleVentaDialog(self.parent, venta_data)
    
    def eliminar_venta(self):
        """Eliminar una venta"""
        selection = self.tree_ventas.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una venta para eliminar")
            return
        
        item = self.tree_ventas.item(selection[0])
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
    
    # ============= MÉTODOS PARA REPARACIONES =============
    
    def filtrar_hoy_rep(self):
        """Filtrar reparaciones de hoy"""
        hoy = datetime.now().strftime('%Y-%m-%d')
        self.fecha_inicio_rep_entry.delete(0, tk.END)
        self.fecha_inicio_rep_entry.insert(0, hoy)
        self.fecha_fin_rep_entry.delete(0, tk.END)
        self.fecha_fin_rep_entry.insert(0, hoy)
    
    def filtrar_mes_rep(self):
        """Filtrar reparaciones de este mes"""
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1).strftime('%Y-%m-%d')
        fin_mes = hoy.strftime('%Y-%m-%d')
        self.fecha_inicio_rep_entry.delete(0, tk.END)
        self.fecha_inicio_rep_entry.insert(0, inicio_mes)
        self.fecha_fin_rep_entry.delete(0, tk.END)
        self.fecha_fin_rep_entry.insert(0, fin_mes)
    
    def limpiar_filtros_rep(self):
        """Limpiar filtros de reparaciones"""
        self.fecha_inicio_rep_entry.delete(0, tk.END)
        self.fecha_fin_rep_entry.delete(0, tk.END)
        self.estado_rep_var.set('todos')
    
    def cargar_reparaciones(self):
        """Cargar reparaciones con filtros"""
        # Limpiar tabla
        for item in self.tree_reparaciones.get_children():
            self.tree_reparaciones.delete(item)
        
        # Obtener filtros
        fecha_inicio = self.fecha_inicio_rep_entry.get().strip() or None
        fecha_fin = self.fecha_fin_rep_entry.get().strip() or None
        estado = self.estado_rep_var.get()
        if estado == 'todos':
            estado = None
        
        # Cargar reparaciones
        reparaciones = self.reparacion_model.obtener_reparaciones(filtro_estado=estado)
        
        # Filtrar por fechas si se especifican
        reparaciones_filtradas = []
        for rep in reparaciones:
            if fecha_inicio or fecha_fin:
                fecha_rep = rep['fecha_creacion'][:10]
                if fecha_inicio and fecha_rep < fecha_inicio:
                    continue
                if fecha_fin and fecha_rep > fecha_fin:
                    continue
            reparaciones_filtradas.append(rep)
        
        # Insertar en tabla
        for rep in reparaciones_filtradas:
            estado_ui = self._estado_db_to_ui(rep['estado'])
            self.tree_reparaciones.insert('', tk.END, values=(
                rep['numero_orden'],
                rep['cliente_nombre'],
                rep['dispositivo'],
                estado_ui,
                f"${rep['sena']:.2f}" if rep['sena'] else '$0.00',
                f"${rep['total']:.2f}",
                rep['fecha_creacion'][:10]
            ))
        
        # Actualizar estadísticas
        self._actualizar_stats_reparaciones(reparaciones_filtradas)
    
    def ver_detalles_reparacion(self):
        """Ver detalles de la reparación seleccionada"""
        selection = self.tree_reparaciones.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione una reparación")
            return
        
        item = self.tree_reparaciones.item(selection[0])
        numero_orden = item['values'][0]
        
        # Obtener reparación
        reparaciones = self.reparacion_model.obtener_reparaciones()
        rep_data = None
        for rep in reparaciones:
            if rep['numero_orden'] == numero_orden:
                rep_data = rep
                break
        
        if not rep_data:
            messagebox.showerror("Error", "No se pudo cargar la reparación")
            return
        
        # Crear ventana de detalles
        DetalleReparacionDialog(self.parent, rep_data)
    
    def _estado_db_to_ui(self, estado_db):
        """Convierte el estado de la base de datos al mostrado en la UI"""
        mapa = {
            'pendiente': 'Pendiente',
            'en_proceso': 'En Proceso',
            'completada': 'Completada',
            'cancelada': 'Cancelada',
        }
        return mapa.get(estado_db, 'Pendiente')
    
    def _actualizar_stats_reparaciones(self, reparaciones):
        """Actualizar estadísticas de reparaciones"""
        total_reparaciones = len(reparaciones)
        total_ingresos = sum(float(rep['total']) for rep in reparaciones if rep['total'])
        total_sena = sum(float(rep['sena']) for rep in reparaciones if rep['sena'])
        
        self.total_reparaciones_label.config(text=str(total_reparaciones))
        self.total_ingresos_rep_label.config(text=f"${total_ingresos:.2f}")
        self.total_sena_label.config(text=f"${total_sena:.2f}")
        
        if total_reparaciones > 0:
            promedio = total_ingresos / total_reparaciones
            self.promedio_rep_label.config(text=f"${promedio:.2f}")
        else:
            self.promedio_rep_label.config(text="$0.00")


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
        
        # Detalles
        tk.Label(main_frame, text="Detalle de Productos:", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W, pady=(10, 5))
        
        columns = ('producto', 'cantidad', 'precio', 'descuento', 'subtotal')
        tree_frame = tk.Frame(main_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)

        tree.heading('producto', text='Producto')
        tree.heading('cantidad', text='Cantidad')
        tree.heading('precio', text='Precio Unit.')
        tree.heading('descuento', text='Descuento')
        tree.heading('subtotal', text='Subtotal')

        tree.column('producto', width=200)
        tree.column('cantidad', width=80, anchor=tk.CENTER)
        tree.column('precio', width=100, anchor=tk.E)
        tree.column('descuento', width=80, anchor=tk.CENTER)
        tree.column('subtotal', width=100, anchor=tk.E)

        for detalle in self.venta_data['detalles']:
            tree.insert('', tk.END, values=(
                detalle[5],  # Producto
                detalle[0],  # Cantidad
                f"${detalle[1]:.2f}",  # Precio
                f"{detalle[2]:.0f}%",  # Descuento
                f"${detalle[4]:.2f}"  # Subtotal
            ))

        # Scrollbar vertical
        scrollbar_v = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_v.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Totales
        totals_frame = tk.Frame(main_frame, bg='white')
        totals_frame.pack(fill=tk.X, pady=10)

        tk.Label(totals_frame, text="Subtotal:", font=("Arial", 11, "bold"), bg='white').grid(row=0, column=0, sticky=tk.E, padx=5)
        tk.Label(totals_frame, text=f"${venta[4]:.2f}", font=("Arial", 11), bg='white').grid(row=0, column=1, sticky=tk.W, padx=5)

        tk.Label(totals_frame, text="Descuento:", font=("Arial", 11, "bold"), bg='white').grid(row=1, column=0, sticky=tk.E, padx=5)
        tk.Label(totals_frame, text=f"${venta[5]:.2f}", font=("Arial", 11), bg='white').grid(row=1, column=1, sticky=tk.W, padx=5)

        tk.Label(totals_frame, text="TOTAL:", font=("Arial", 13, "bold"), bg='white').grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        tk.Label(totals_frame, text=f"${venta[6]:.2f}", font=("Arial", 13, "bold"), fg="green", bg='white').grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)


class DetalleReparacionDialog:
    def __init__(self, parent, rep_data):
        self.rep_data = rep_data
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Detalle de Reparación")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 300
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 250
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.create_widgets()

    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        main_frame = tk.Frame(self.dialog, bg='white', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información de la reparación
        info_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(info_frame, text="Información de la Reparación", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"N° Orden: {self.rep_data['numero_orden']}", font=("Arial", 12, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Cliente: {self.rep_data['cliente_nombre']}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Teléfono: {self.rep_data['cliente_telefono'] or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Email: {self.rep_data['cliente_email'] or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        
        # Dispositivo
        device_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(device_frame, text="Dispositivo", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(device_frame, text=f"Tipo: {self.rep_data['dispositivo']}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(device_frame, text=f"Modelo: {self.rep_data['modelo'] or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(device_frame, text=f"N° Serie: {self.rep_data['numero_serie'] or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        
        # Problema y observaciones
        problem_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        problem_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(problem_frame, text="Problema:", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(problem_frame, text=self.rep_data['problema'] or 'N/A', bg='white', fg='black', wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, fill=tk.BOTH, expand=True)
        
        tk.Label(problem_frame, text="Observaciones:", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W, pady=(10, 0))
        tk.Label(problem_frame, text=self.rep_data['observaciones'] or 'N/A', bg='white', fg='black', wraplength=500, justify=tk.LEFT).pack(anchor=tk.W, fill=tk.BOTH, expand=True)
        
        # Precios y estado
        prices_frame = tk.Frame(main_frame, bg='white')
        prices_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(prices_frame, text="Seña:", font=("Arial", 11, "bold"), bg='white').grid(row=0, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=f"${self.rep_data['sena']:.2f}" if self.rep_data['sena'] else "$0.00", font=("Arial", 11), bg='white').grid(row=0, column=1, sticky=tk.W, padx=5)
        
        tk.Label(prices_frame, text="Total:", font=("Arial", 11, "bold"), bg='white').grid(row=0, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=f"${self.rep_data['total']:.2f}", font=("Arial", 11, "bold"), fg="green", bg='white').grid(row=0, column=3, sticky=tk.W, padx=5)
        
        estado_ui = self._estado_db_to_ui(self.rep_data['estado'])
        tk.Label(prices_frame, text="Estado:", font=("Arial", 11, "bold"), bg='white').grid(row=1, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=estado_ui, font=("Arial", 11), bg='white').grid(row=1, column=1, sticky=tk.W, padx=5)
        
        tk.Label(prices_frame, text="Fecha:", font=("Arial", 11, "bold"), bg='white').grid(row=1, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=self.rep_data['fecha_creacion'][:10], font=("Arial", 11), bg='white').grid(row=1, column=3, sticky=tk.W, padx=5)
    
    def _estado_db_to_ui(self, estado_db):
        """Convierte el estado de la base de datos al mostrado en la UI"""
        mapa = {
            'pendiente': 'Pendiente',
            'en_proceso': 'En Proceso',
            'completada': 'Completada',
            'cancelada': 'Cancelada',
        }
        return mapa.get(estado_db, 'Pendiente')

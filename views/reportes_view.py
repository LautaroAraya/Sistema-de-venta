import tkinter as tk
from tkinter import ttk, messagebox
from models.venta import Venta
from models.reparacion import Reparacion
from datetime import datetime, timedelta
import calendar
import math

class ReportesView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.venta_model = Venta(db_manager)
        self.reparacion_model = Reparacion(db_manager)
        self.reporte_final_interval_ms = 15 * 60 * 1000
        self._reporte_final_job = None
        
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
        
        # Pestaña de Ventas de Celulares
        celulares_frame = ttk.Frame(notebook)
        notebook.add(celulares_frame, text="📱 Ventas Celulares")
        self.crear_tab_ventas_celulares(celulares_frame)

        # Pestaña de Reporte Final
        reporte_final_frame = ttk.Frame(notebook)
        notebook.add(reporte_final_frame, text="📈 Reporte Final")
        self.crear_tab_reporte_final(reporte_final_frame)
        
        # Cargar reparaciones automáticamente
        self.cargar_reparaciones()
        self.cargar_ventas_celulares()
        self.actualizar_reporte_final()
    
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
        
        # Botones de filtro rápido
        tk.Button(filter_frame, text="Hoy", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_hoy_rep).grid(row=1, column=4, padx=5, pady=5)
        tk.Button(filter_frame, text="Este Mes", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_mes_rep).grid(row=1, column=5, padx=5, pady=5)
        tk.Button(filter_frame, text="Limpiar", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.limpiar_filtros_rep).grid(row=1, column=6, padx=5, pady=5)
        
        # Aplicar filtros
        tk.Button(filter_frame, text="Aplicar", font=("Arial", 9), bg='#2563EB', fg='white', relief=tk.RAISED,
                  command=self.cargar_reparaciones).grid(row=1, column=7, padx=5, pady=5)
        
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
        columns = ('numero', 'cliente', 'dispositivo', 'estado', 'sena', 'total', 'fecha', 'estado_pago', 'fecha_pago', 'medio_pago', 'recargo_pct')
        self.tree_reparaciones = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        self.tree_reparaciones.heading('numero', text='N° Orden')
        self.tree_reparaciones.heading('cliente', text='Cliente')
        self.tree_reparaciones.heading('dispositivo', text='Dispositivo')
        self.tree_reparaciones.heading('estado', text='Estado')
        self.tree_reparaciones.heading('sena', text='Seña')
        self.tree_reparaciones.heading('total', text='Total')
        self.tree_reparaciones.heading('fecha', text='Fecha')
        self.tree_reparaciones.heading('estado_pago', text='Estado')
        self.tree_reparaciones.heading('fecha_pago', text='Fecha Pago')
        self.tree_reparaciones.heading('medio_pago', text='Medio Pago')
        self.tree_reparaciones.heading('recargo_pct', text='Recargo %')
        
        self.tree_reparaciones.column('numero', width=120)
        self.tree_reparaciones.column('cliente', width=180)
        self.tree_reparaciones.column('dispositivo', width=120)
        self.tree_reparaciones.column('estado', width=100)
        self.tree_reparaciones.column('sena', width=100, anchor=tk.E)
        self.tree_reparaciones.column('total', width=100, anchor=tk.E)
        self.tree_reparaciones.column('fecha', width=130)
        self.tree_reparaciones.column('estado_pago', width=160)
        self.tree_reparaciones.column('fecha_pago', width=110)
        self.tree_reparaciones.column('medio_pago', width=120)
        self.tree_reparaciones.column('recargo_pct', width=90, anchor=tk.E)

        self.tree_reparaciones.tag_configure('pago_ok', foreground='#10B981')
        self.tree_reparaciones.tag_configure('pago_debe', foreground='#EF4444')
        
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
        self.cargar_reparaciones()
    
    def filtrar_mes_rep(self):
        """Filtrar reparaciones de este mes"""
        hoy = datetime.now()
        inicio_mes = hoy.replace(day=1).strftime('%Y-%m-%d')
        fin_mes = hoy.strftime('%Y-%m-%d')
        self.fecha_inicio_rep_entry.delete(0, tk.END)
        self.fecha_inicio_rep_entry.insert(0, inicio_mes)
        self.fecha_fin_rep_entry.delete(0, tk.END)
        self.fecha_fin_rep_entry.insert(0, fin_mes)
        self.cargar_reparaciones()
    
    def limpiar_filtros_rep(self):
        """Limpiar filtros de reparaciones"""
        self.fecha_inicio_rep_entry.delete(0, tk.END)
        self.fecha_fin_rep_entry.delete(0, tk.END)
        self.cargar_reparaciones()
    
    def cargar_reparaciones(self):
        """Cargar reparaciones con filtros - solo con seña o retiradas"""
        # Limpiar tabla
        for item in self.tree_reparaciones.get_children():
            self.tree_reparaciones.delete(item)
        
        # Obtener filtros
        fecha_inicio = self.fecha_inicio_rep_entry.get().strip() or None
        fecha_fin = self.fecha_fin_rep_entry.get().strip() or None
        
        # Cargar todas las reparaciones (sin filtro de estado)
        reparaciones = self.reparacion_model.obtener_reparaciones(filtro_estado=None)
        
        # Filtrar: solo mostrar reparaciones con seña O en estado retirado
        reparaciones_filtradas = []
        for rep in reparaciones:
            # Condición: tiene seña (sena > 0) O está retirada
            if rep['sena'] and rep['sena'] > 0 or rep['estado'] == 'retirado':
                # Filtrar por fechas si se especifican
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
            total = float(rep.get('total') or 0)
            sena = float(rep.get('sena') or 0)
            monto_final = float(rep.get('monto_pago_final') or 0)
            pagado_total = sena + monto_final
            saldo = total - pagado_total
            if saldo <= 0:
                estado_pago_texto = f"Pagado: ${monto_final:.2f}"
                tag = 'pago_ok'
            else:
                estado_pago_texto = f"Debe ${saldo:.2f}"
                tag = 'pago_debe'

            fecha_pago = rep.get('fecha_pago_final')
            fecha_pago = fecha_pago[:10] if fecha_pago else 'Pendiente'
            medio_pago = rep.get('medio_pago_final') or 'Pendiente'
            medio_pago = medio_pago.capitalize() if medio_pago != 'Pendiente' else medio_pago
            recargo_monto = float(rep.get('recargo_tarjeta') or 0)
            base_tarjeta = max(monto_final - recargo_monto, 0)
            recargo_pct = (recargo_monto / base_tarjeta * 100) if base_tarjeta > 0 else 0
            recargo_texto = f"{recargo_pct:.2f}%"
            self.tree_reparaciones.insert('', tk.END, values=(
                rep['numero_orden'],
                rep['cliente_nombre'],
                rep['dispositivo'],
                estado_ui,
                f"${sena:.2f}" if sena else '$0.00',
                f"${total:.2f}",
                rep['fecha_creacion'][:10],
                estado_pago_texto,
                fecha_pago,
                medio_pago,
                recargo_texto
            ), tags=(tag,))
        
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
        DetalleReparacionDialog(self.parent, rep_data, self)
    
    def _estado_db_to_ui(self, estado_db):
        """Convierte el estado de la base de datos al mostrado en la UI - Primera función"""
        mapa = {
            'en_proceso': 'En Proceso',
            'en_espera_retiro': 'En Espera de Retiro',
            'retirado': 'Retirado',
        }
        return mapa.get(estado_db, 'En Proceso')
    
    def _actualizar_stats_reparaciones(self, reparaciones):
        """Actualizar estadísticas de reparaciones"""
        total_reparaciones = len(reparaciones)
        total_sena = sum(float(rep.get('sena') or 0) for rep in reparaciones)
        total_pago_final = sum(float(rep.get('monto_pago_final') or 0) for rep in reparaciones)
        total_ingresos = total_sena + total_pago_final
        
        self.total_reparaciones_label.config(text=str(total_reparaciones))
        self.total_ingresos_rep_label.config(text=f"${total_ingresos:.2f}")
        self.total_sena_label.config(text=f"${total_sena:.2f}")
        
        if total_reparaciones > 0:
            promedio = total_ingresos / total_reparaciones
            self.promedio_rep_label.config(text=f"${promedio:.2f}")
        else:
            self.promedio_rep_label.config(text="$0.00")
    
    def crear_tab_ventas_celulares(self, parent):
        """Crear la pestaña de ventas de celulares"""
        # Frame de filtros
        filter_frame = tk.Frame(parent, bg='white')
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filtros", font=("Arial", 11, "bold"), bg='white', fg='black').grid(row=0, column=0, columnspan=8, sticky=tk.W, padx=5, pady=5)
        
        # Fecha inicio
        tk.Label(filter_frame, text="Desde:", bg='white', fg='black').grid(row=1, column=0, padx=5, pady=5)
        self.fecha_inicio_cel_entry = tk.Entry(filter_frame, width=15)
        self.fecha_inicio_cel_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Fecha fin
        tk.Label(filter_frame, text="Hasta:", bg='white', fg='black').grid(row=1, column=2, padx=5, pady=5)
        self.fecha_fin_cel_entry = tk.Entry(filter_frame, width=15)
        self.fecha_fin_cel_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Botones de filtro rápido
        tk.Button(filter_frame, text="Hoy", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_hoy_cel).grid(row=1, column=4, padx=5, pady=5)
        tk.Button(filter_frame, text="Este Mes", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.filtrar_mes_cel).grid(row=1, column=5, padx=5, pady=5)
        
        # Botones
        tk.Button(filter_frame, text="Limpiar", font=("Arial", 9), bg='white', fg='black', relief=tk.RAISED,
                  command=self.limpiar_filtros_cel).grid(row=1, column=6, padx=5, pady=5)
        tk.Button(filter_frame, text="Aplicar", font=("Arial", 9), bg='#2563EB', fg='white', relief=tk.RAISED,
                  command=self.cargar_ventas_celulares).grid(row=1, column=7, padx=5, pady=5)
        
        # Estadísticas
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stats_frame, text="Estadísticas", font=("Arial", 11, "bold"), bg='white', fg='black').grid(row=0, column=0, columnspan=6, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(stats_frame, text="Total Ventas:", bg='white', fg='black').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.total_ventas_cel_label = tk.Label(stats_frame, text="0", font=("Arial", 11, "bold"), bg='white', fg='black')
        self.total_ventas_cel_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        tk.Label(stats_frame, text="Total Ingresos:", bg='white', fg='black').grid(row=1, column=2, sticky=tk.W, padx=20)
        self.total_ingresos_cel_label = tk.Label(stats_frame, text="$0.00", font=("Arial", 11, "bold"), bg='white', fg='#10B981')
        self.total_ingresos_cel_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        tk.Label(stats_frame, text="Total Seña:", bg='white', fg='black').grid(row=1, column=4, sticky=tk.W, padx=20)
        self.total_sena_cel_label = tk.Label(stats_frame, text="$0.00", font=("Arial", 11, "bold"), bg='white', fg='#F59E0B')
        self.total_sena_cel_label.grid(row=1, column=5, sticky=tk.W, padx=5)
        
        # Tabla de ventas de celulares
        columns = ('numero', 'cliente', 'telefono', 'marca', 'modelo', 'sena', 'total', 'fecha', 'estado_pago', 'fecha_pago', 'medio_pago', 'recargo_pct')
        self.tree_ventas_cel = ttk.Treeview(parent, columns=columns, show='headings', height=15)
        
        headings = ['N° Venta', 'Cliente', 'Teléfono', 'Marca', 'Modelo', 'Seña', 'Total', 'Fecha', 'Estado', 'Fecha Pago', 'Medio Pago', 'Recargo %']
        for col, head in zip(columns, headings):
            self.tree_ventas_cel.heading(col, text=head)
        
        self.tree_ventas_cel.column('numero', width=120)
        self.tree_ventas_cel.column('cliente', width=140)
        self.tree_ventas_cel.column('telefono', width=100)
        self.tree_ventas_cel.column('marca', width=100)
        self.tree_ventas_cel.column('modelo', width=100)
        self.tree_ventas_cel.column('sena', width=90, anchor=tk.E)
        self.tree_ventas_cel.column('total', width=90, anchor=tk.E)
        self.tree_ventas_cel.column('fecha', width=100)
        self.tree_ventas_cel.column('estado_pago', width=150)
        self.tree_ventas_cel.column('fecha_pago', width=100)
        self.tree_ventas_cel.column('medio_pago', width=110)
        self.tree_ventas_cel.column('recargo_pct', width=90, anchor=tk.E)

        self.tree_ventas_cel.tag_configure('pago_ok', foreground='#10B981')
        self.tree_ventas_cel.tag_configure('pago_debe', foreground='#EF4444')
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree_ventas_cel.yview)
        scrollbar_h = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.tree_ventas_cel.xview)
        self.tree_ventas_cel.config(yscrollcommand=scrollbar.set, xscrollcommand=scrollbar_h.set)
        
        # Evento doble clic para ver detalle
        self.tree_ventas_cel.bind('<Double-Button-1>', lambda e: self.ver_detalle_venta_celular())
        
        self.tree_ventas_cel.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(fill=tk.X)

    def crear_tab_reporte_final(self, parent):
        """Crear la pestaña de reporte final"""
        header_frame = tk.Frame(parent, bg='white')
        header_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            header_frame,
            text="Reporte Final - Totales por Mes",
            font=("Arial", 12, "bold"),
            bg='white',
            fg='black'
        ).pack(anchor=tk.W)

        tk.Label(
            header_frame,
            text="Selecciona un mes para ver la distribucion por tipo",
            font=("Arial", 9),
            bg='white',
            fg='gray'
        ).pack(anchor=tk.W)

        selector_frame = tk.Frame(parent, bg='white')
        selector_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(selector_frame, text="Mes:", bg='white', fg='black').pack(side=tk.LEFT)

        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        self.reporte_final_mes_var = tk.StringVar(value=meses[datetime.now().month - 1])
        self.reporte_final_mes_combo = ttk.Combobox(
            selector_frame,
            values=meses,
            textvariable=self.reporte_final_mes_var,
            state="readonly",
            width=14
        )
        self.reporte_final_mes_combo.pack(side=tk.LEFT, padx=6)
        self.reporte_final_mes_combo.bind("<<ComboboxSelected>>", lambda e: self.actualizar_reporte_final())

        content_frame = tk.Frame(parent, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.reporte_final_canvas = tk.Canvas(content_frame, width=360, height=260, bg='white', highlightthickness=0)
        self.reporte_final_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 20))
        self.reporte_final_canvas.bind("<Motion>", self._on_reporte_final_motion)
        self.reporte_final_canvas.bind("<Leave>", self._on_reporte_final_leave)

        legend_frame = tk.Frame(content_frame, bg='white')
        legend_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.reporte_final_labels = {}
        for label_text in ["Ventas", "Reparaciones", "Ventas Celulares"]:
            row = tk.Frame(legend_frame, bg='white')
            row.pack(anchor=tk.W, pady=4)

            color_box = tk.Canvas(row, width=14, height=14, bg='white', highlightthickness=0)
            color_box.pack(side=tk.LEFT, padx=(0, 6))

            text_label = tk.Label(row, text=f"{label_text}: $0.00", bg='white', fg='black', font=("Arial", 10, "bold"))
            text_label.pack(side=tk.LEFT)

            self.reporte_final_labels[label_text] = (color_box, text_label)

        self.reporte_final_tooltip = tk.Label(
            content_frame,
            text="",
            bg="#111827",
            fg="white",
            font=("Arial", 9),
            padx=6,
            pady=3
        )
        self.reporte_final_tooltip.place_forget()

    def actualizar_reporte_final(self):
        """Actualizar datos y grafico del reporte final"""
        totales = self._obtener_totales_mes()
        self._dibujar_grafico_torta(totales)
        self._programar_actualizacion_reporte_final()

    def _programar_actualizacion_reporte_final(self):
        """Reprogramar la actualizacion automatica"""
        if self._reporte_final_job is not None:
            self.parent.after_cancel(self._reporte_final_job)
        self._reporte_final_job = self.parent.after(
            self.reporte_final_interval_ms,
            self.actualizar_reporte_final
        )

    def _obtener_totales_mes(self):
        """Calcular totales del mes seleccionado (anio actual) para cada tipo"""
        meses = {
            "Enero": 1, "Febrero": 2, "Marzo": 3, "Abril": 4, "Mayo": 5, "Junio": 6,
            "Julio": 7, "Agosto": 8, "Septiembre": 9, "Octubre": 10, "Noviembre": 11, "Diciembre": 12
        }
        hoy = datetime.now()
        mes_nombre = self.reporte_final_mes_var.get()
        mes_num = meses.get(mes_nombre, hoy.month)
        anio = hoy.year
        ultimo_dia = calendar.monthrange(anio, mes_num)[1]
        inicio_mes = f"{anio:04d}-{mes_num:02d}-01"
        fin_mes = f"{anio:04d}-{mes_num:02d}-{ultimo_dia:02d}"

        stats_ventas = self.venta_model.obtener_estadisticas(inicio_mes, fin_mes)
        total_ventas = float(stats_ventas[1] or 0) if stats_ventas else 0.0

        reparaciones = self.reparacion_model.obtener_reparaciones(filtro_estado=None)
        total_reparaciones = 0.0
        for rep in reparaciones:
            if not (rep.get('sena') and rep.get('sena') > 0 or rep.get('estado') == 'retirado'):
                continue
            fecha_rep = (rep.get('fecha_creacion') or '')[:10]
            if fecha_rep < inicio_mes or fecha_rep > fin_mes:
                continue
            total_reparaciones += float(rep.get('sena') or 0) + float(rep.get('monto_pago_final') or 0)

        total_celulares = 0.0
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                SELECT
                    COALESCE(SUM(sena), 0) + COALESCE(SUM(monto_pago_final), 0)
                FROM ventas_celulares
                WHERE DATE(fecha_venta) >= ? AND DATE(fecha_venta) <= ?
            ''', (inicio_mes, fin_mes))
            result = cursor.fetchone()
            if result:
                total_celulares = float(result[0] or 0)
        except Exception:
            total_celulares = 0.0

        return {
            "Ventas": total_ventas,
            "Reparaciones": total_reparaciones,
            "Ventas Celulares": total_celulares
        }

    def _dibujar_grafico_torta(self, totales):
        """Dibujar grafico de torta con totales"""
        self.reporte_final_canvas.delete("all")
        colores = {
            "Ventas": "#10B981",
            "Reparaciones": "#F59E0B",
            "Ventas Celulares": "#3B82F6"
        }

        total = sum(totales.values())
        self._reporte_final_slices = []
        if total <= 0:
            self.reporte_final_canvas.create_text(
                180, 130,
                text="Sin datos para el mes",
                fill="gray",
                font=("Arial", 11, "bold")
            )
        else:
            start_angle = 0
            box = (20, 20, 240, 240)
            for key, value in totales.items():
                extent = (value / total) * 360
                self.reporte_final_canvas.create_arc(
                    box,
                    start=start_angle,
                    extent=extent,
                    fill=colores.get(key, "#9CA3AF"),
                    outline="white"
                )
                self._reporte_final_slices.append({
                    "label": key,
                    "value": value,
                    "start": start_angle,
                    "extent": extent,
                    "color": colores.get(key, "#9CA3AF")
                })
                start_angle += extent

        for key, value in totales.items():
            color_box, text_label = self.reporte_final_labels.get(key, (None, None))
            if color_box is not None:
                color_box.delete("all")
                color_box.create_rectangle(0, 0, 14, 14, fill=colores.get(key, "#9CA3AF"), outline='')
            if text_label is not None:
                text_label.config(text=f"{key}: ${value:.2f}")

    def _on_reporte_final_motion(self, event):
        """Mostrar tooltip al pasar sobre una porcion"""
        if not hasattr(self, "_reporte_final_slices"):
            return
        cx, cy = 130, 130
        dx = event.x - cx
        dy = event.y - cy
        distancia = (dx ** 2 + dy ** 2) ** 0.5
        if distancia > 110 or distancia < 5:
            self.reporte_final_tooltip.place_forget()
            return

        angulo = (360 - (math.degrees(math.atan2(dy, dx)) % 360)) % 360
        for slice_info in self._reporte_final_slices:
            start = slice_info["start"]
            end = start + slice_info["extent"]
            if start <= angulo < end:
                texto = f"{slice_info['label']}: ${slice_info['value']:.2f}"
                self.reporte_final_tooltip.config(text=texto)
                self.reporte_final_tooltip.place(x=event.x + 10, y=event.y + 10)
                return
        self.reporte_final_tooltip.place_forget()

    def _on_reporte_final_leave(self, _event):
        """Ocultar tooltip al salir"""
        self.reporte_final_tooltip.place_forget()
    
    def cargar_ventas_celulares(self):
        """Cargar ventas de celulares con filtros"""
        for item in self.tree_ventas_cel.get_children():
            self.tree_ventas_cel.delete(item)
        
        fecha_inicio = self.fecha_inicio_cel_entry.get().strip() or None
        fecha_fin = self.fecha_fin_cel_entry.get().strip() or None
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT numero_venta, cliente_nombre, cliente_telefono, telefono_marca, 
                       telefono_modelo, sena, total, fecha_venta,
                       fecha_pago_final, medio_pago_final, monto_pago_final, recargo_tarjeta
                FROM ventas_celulares
                ORDER BY fecha_venta DESC
                LIMIT 100
            ''')
            
            ventas = cursor.fetchall()
            ventas_filtradas = []
            
            for venta in ventas:
                if fecha_inicio or fecha_fin:
                    fecha_venta = venta[7][:10] if venta[7] else ''
                    if fecha_inicio and fecha_venta < fecha_inicio:
                        continue
                    if fecha_fin and fecha_venta > fecha_fin:
                        continue
                ventas_filtradas.append(venta)
            
            # Insertar en tabla
            for venta in ventas_filtradas:
                fecha = venta[7][:10] if venta[7] else 'N/A'
                sena = float(venta[5] or 0)
                total = float(venta[6] or 0)
                fecha_pago = venta[8][:10] if venta[8] else 'Pendiente'
                medio_pago = venta[9] or 'Pendiente'
                medio_pago = medio_pago.capitalize() if medio_pago != 'Pendiente' else medio_pago
                monto_pago_final = float(venta[10] or 0)
                recargo_monto = float(venta[11] or 0)
                base_tarjeta = max(monto_pago_final - recargo_monto, 0)
                recargo_pct = (recargo_monto / base_tarjeta * 100) if base_tarjeta > 0 else 0
                recargo_texto = f"{recargo_pct:.2f}%"

                saldo = total - (sena + monto_pago_final)
                if saldo <= 0:
                    estado_pago_texto = f"Pagado: ${monto_pago_final:.2f}"
                    tag = 'pago_ok'
                else:
                    estado_pago_texto = f"Debe ${saldo:.2f}"
                    tag = 'pago_debe'

                self.tree_ventas_cel.insert('', 'end', values=(
                    venta[0],  # numero_venta
                    venta[1],  # cliente_nombre
                    venta[2] or '',  # cliente_telefono
                    venta[3] or '',  # telefono_marca
                    venta[4] or '',  # telefono_modelo
                    f"${sena:.2f}" if sena else '$0.00',  # sena
                    f"${total:.2f}",  # total
                    fecha,
                    estado_pago_texto,
                    fecha_pago,
                    medio_pago,
                    recargo_texto
                ), tags=(tag,))
            
            # Actualizar estadísticas
            total_ventas = len(ventas_filtradas)
            total_sena = sum(float(v[5] or 0) for v in ventas_filtradas)
            total_pago_final = sum(float(v[10] or 0) for v in ventas_filtradas)
            total_ingresos = total_sena + total_pago_final
            
            self.total_ventas_cel_label.config(text=str(total_ventas))
            self.total_ingresos_cel_label.config(text=f"${total_ingresos:.2f}")
            self.total_sena_cel_label.config(text=f"${total_sena:.2f}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ventas de celulares: {str(e)}")
    
    def limpiar_filtros_cel(self):
        """Limpiar filtros de ventas de celulares"""
        self.fecha_inicio_cel_entry.delete(0, tk.END)
        self.fecha_fin_cel_entry.delete(0, tk.END)
        self.cargar_ventas_celulares()
    
    def filtrar_hoy_cel(self):
        """Filtrar ventas de celulares por hoy"""
        hoy = datetime.now().strftime('%Y-%m-%d')
        self.fecha_inicio_cel_entry.delete(0, tk.END)
        self.fecha_fin_cel_entry.delete(0, tk.END)
        self.fecha_inicio_cel_entry.insert(0, hoy)
        self.fecha_fin_cel_entry.insert(0, hoy)
        self.cargar_ventas_celulares()
    
    def filtrar_mes_cel(self):
        """Filtrar ventas de celulares por este mes"""
        hoy = datetime.now()
        primer_dia = hoy.replace(day=1).strftime('%Y-%m-%d')
        ultimo_dia = hoy.strftime('%Y-%m-%d')
        self.fecha_inicio_cel_entry.delete(0, tk.END)
        self.fecha_fin_cel_entry.delete(0, tk.END)
        self.fecha_inicio_cel_entry.insert(0, primer_dia)
        self.fecha_fin_cel_entry.insert(0, ultimo_dia)
        self.cargar_ventas_celulares()
    
    def ver_detalle_venta_celular(self):
        """Ver detalle de venta de celular seleccionada"""
        selection = self.tree_ventas_cel.selection()
        if not selection:
            return
        
        item = self.tree_ventas_cel.item(selection[0])
        numero_venta = item['values'][0]
        
        # Obtener datos completos de la venta
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT v.*, u.nombre_completo as vendedor
                FROM ventas_celulares v
                LEFT JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.numero_venta = ?
            ''', (numero_venta,))
            
            venta = cursor.fetchone()
            if venta:
                DetalleVentaCelularDialog(self.parent, dict(venta), self.db_manager)
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener detalle de venta: {str(e)}")


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
    def __init__(self, parent, rep_data, reportes_view):
        self.rep_data = rep_data
        self.reportes_view = reportes_view
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Detalle de Reparación")
        self.dialog.geometry("650x700")
        self.dialog.transient(parent)
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 325
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 350
        self.dialog.geometry(f"650x700+{x}+{y}")
        
        self.create_widgets()

    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        
        # Canvas con scrollbar
        canvas = tk.Canvas(self.dialog, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Contenido
        main_frame = tk.Frame(scrollable_frame, bg='white')
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
        problem_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(problem_frame, text="Problema:", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(problem_frame, text=self.rep_data['problema'] or 'N/A', bg='white', fg='black', wraplength=550, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Label(problem_frame, text="Observaciones:", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(problem_frame, text=self.rep_data['observaciones'] or 'N/A', bg='white', fg='black', wraplength=550, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Precios y estado
        prices_frame = tk.Frame(main_frame, bg='white')
        prices_frame.pack(fill=tk.X, pady=10)
        
        recargo_monto = float(self.rep_data.get('recargo_tarjeta') or 0)
        total_base = float(self.rep_data.get('total') or 0)
        total_con_recargo = total_base + recargo_monto

        tk.Label(prices_frame, text="Seña:", font=("Arial", 11, "bold"), bg='white').grid(row=0, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=f"${self.rep_data['sena']:.2f}" if self.rep_data['sena'] else "$0.00", font=("Arial", 11), bg='white').grid(row=0, column=1, sticky=tk.W, padx=5)

        tk.Label(prices_frame, text="Total:", font=("Arial", 11, "bold"), bg='white').grid(row=0, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=f"${total_con_recargo:.2f}", font=("Arial", 11, "bold"), fg="green", bg='white').grid(row=0, column=3, sticky=tk.W, padx=5)
        
        estado_ui = self.reportes_view._estado_db_to_ui(self.rep_data['estado'])
        tk.Label(prices_frame, text="Estado:", font=("Arial", 11, "bold"), bg='white').grid(row=1, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=estado_ui, font=("Arial", 11), bg='white').grid(row=1, column=1, sticky=tk.W, padx=5)
        
        tk.Label(prices_frame, text="Fecha:", font=("Arial", 11, "bold"), bg='white').grid(row=1, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=self.rep_data['fecha_creacion'][:10], font=("Arial", 11), bg='white').grid(row=1, column=3, sticky=tk.W, padx=5)

        fecha_pago = self.rep_data.get('fecha_pago_final')
        fecha_pago = fecha_pago[:10] if fecha_pago else 'Pendiente'
        medio_pago = self.rep_data.get('medio_pago_final') or 'Pendiente'
        medio_pago = medio_pago.capitalize() if medio_pago != 'Pendiente' else medio_pago
        monto_pago_final = float(self.rep_data.get('monto_pago_final') or 0)
        base_tarjeta = max(monto_pago_final - recargo_monto, 0)
        recargo_pct = (recargo_monto / base_tarjeta * 100) if base_tarjeta > 0 else 0

        tk.Label(prices_frame, text="Pago Final:", font=("Arial", 11, "bold"), bg='white').grid(row=2, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=f"${monto_pago_final:.2f}", font=("Arial", 11), bg='white').grid(row=2, column=1, sticky=tk.W, padx=5)

        tk.Label(prices_frame, text="Fecha Pago:", font=("Arial", 11, "bold"), bg='white').grid(row=2, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=fecha_pago, font=("Arial", 11), bg='white').grid(row=2, column=3, sticky=tk.W, padx=5)

        tk.Label(prices_frame, text="Medio Pago:", font=("Arial", 11, "bold"), bg='white').grid(row=3, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=medio_pago, font=("Arial", 11), bg='white').grid(row=3, column=1, sticky=tk.W, padx=5)

        tk.Label(prices_frame, text="Recargo %:", font=("Arial", 11, "bold"), bg='white').grid(row=3, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=f"{recargo_pct:.2f}%", font=("Arial", 11), bg='white').grid(row=3, column=3, sticky=tk.W, padx=5)
        
        # Botón cerrar
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Cerrar", font=('Arial', 10), bg='#6B7280', fg='white',
                 width=15, command=self.dialog.destroy).pack()


class DetalleVentaCelularDialog:
    def __init__(self, parent, venta_data, db_manager):
        self.venta_data = venta_data
        self.db_manager = db_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Detalle de Venta de Celular")
        self.dialog.geometry("650x650")
        self.dialog.transient(parent)
        
        # Centrar diálogo
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 325
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 325
        self.dialog.geometry(f"650x650+{x}+{y}")
        
        self.create_widgets()

    def create_widgets(self):
        """Crear widgets"""
        self.dialog.configure(bg='white')
        
        # Canvas con scrollbar
        canvas = tk.Canvas(self.dialog, bg='white', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.dialog, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Contenido
        main_frame = tk.Frame(scrollable_frame, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información de la venta
        info_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(info_frame, text="Información de la Venta", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"N° Venta: {self.venta_data.get('numero_venta', 'N/A')}", font=("Arial", 12, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Fecha: {self.venta_data.get('fecha_venta', 'N/A')[:16] if self.venta_data.get('fecha_venta') else 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Vendedor: {self.venta_data.get('vendedor', 'N/A')}", bg='white', fg='black').pack(anchor=tk.W)
        
        # Cliente
        cliente_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        cliente_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(cliente_frame, text="Cliente", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(cliente_frame, text=f"Nombre: {self.venta_data.get('cliente_nombre') or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(cliente_frame, text=f"Documento: {self.venta_data.get('cliente_documento') or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(cliente_frame, text=f"Teléfono: {self.venta_data.get('cliente_telefono') or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(cliente_frame, text=f"Email: {self.venta_data.get('cliente_email') or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        
        # Teléfono vendido
        telefono_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
        telefono_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(telefono_frame, text="Teléfono Vendido", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(telefono_frame, text=f"Marca: {self.venta_data.get('telefono_marca') or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        tk.Label(telefono_frame, text=f"Modelo: {self.venta_data.get('telefono_modelo') or 'N/A'}", bg='white', fg='black').pack(anchor=tk.W)
        
        # Descripción
        if self.venta_data.get('descripcion'):
            desc_frame = tk.Frame(main_frame, bg='white', relief=tk.RIDGE, bd=1, padx=10, pady=10)
            desc_frame.pack(fill=tk.X, pady=(0, 10))
            
            tk.Label(desc_frame, text="Descripción:", font=("Arial", 11, "bold"), bg='white', fg='black').pack(anchor=tk.W)
            tk.Label(desc_frame, text=self.venta_data.get('descripcion'), bg='white', fg='black', wraplength=550, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Precios
        prices_frame = tk.Frame(main_frame, bg='white')
        prices_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(prices_frame, text="Seña:", font=("Arial", 11, "bold"), bg='white').grid(row=0, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=f"${self.venta_data.get('sena', 0):.2f}", font=("Arial", 11), bg='white').grid(row=0, column=1, sticky=tk.W, padx=5)
        
        recargo_monto = float(self.venta_data.get('recargo_tarjeta') or 0)
        total_base = float(self.venta_data.get('total') or 0)
        total_con_recargo = total_base + recargo_monto

        tk.Label(prices_frame, text="Total:", font=("Arial", 11, "bold"), bg='white').grid(row=0, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=f"${total_con_recargo:.2f}", font=("Arial", 11, "bold"), fg="#10B981", bg='white').grid(row=0, column=3, sticky=tk.W, padx=5)

        fecha_pago = self.venta_data.get('fecha_pago_final')
        fecha_pago = fecha_pago[:10] if fecha_pago else 'Pendiente'
        medio_pago = self.venta_data.get('medio_pago_final') or 'Pendiente'
        medio_pago = medio_pago.capitalize() if medio_pago != 'Pendiente' else medio_pago
        monto_pago_final = float(self.venta_data.get('monto_pago_final') or 0)
        base_tarjeta = max(monto_pago_final - recargo_monto, 0)
        recargo_pct = (recargo_monto / base_tarjeta * 100) if base_tarjeta > 0 else 0

        tk.Label(prices_frame, text="Pago Final:", font=("Arial", 11, "bold"), bg='white').grid(row=1, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=f"${monto_pago_final:.2f}", font=("Arial", 11), bg='white').grid(row=1, column=1, sticky=tk.W, padx=5)

        tk.Label(prices_frame, text="Fecha Pago:", font=("Arial", 11, "bold"), bg='white').grid(row=1, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=fecha_pago, font=("Arial", 11), bg='white').grid(row=1, column=3, sticky=tk.W, padx=5)

        tk.Label(prices_frame, text="Medio Pago:", font=("Arial", 11, "bold"), bg='white').grid(row=2, column=0, sticky=tk.E, padx=5)
        tk.Label(prices_frame, text=medio_pago, font=("Arial", 11), bg='white').grid(row=2, column=1, sticky=tk.W, padx=5)

        tk.Label(prices_frame, text="Recargo %:", font=("Arial", 11, "bold"), bg='white').grid(row=2, column=2, sticky=tk.E, padx=20)
        tk.Label(prices_frame, text=f"{recargo_pct:.2f}%", font=("Arial", 11), bg='white').grid(row=2, column=3, sticky=tk.W, padx=5)
        
        # Botón cerrar
        btn_frame = tk.Frame(main_frame, bg='white')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Cerrar", font=('Arial', 10), bg='#6B7280', fg='white',
                 width=15, command=self.dialog.destroy).pack()

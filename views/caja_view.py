import tkinter as tk
from tkinter import ttk, messagebox
from models.caja import Caja
from datetime import datetime

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
        
        # Título con color
        title_frame = tk.Frame(self.parent, bg='#8B5CF6', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)
        
        tk.Label(title_frame,
                text="💰 GESTIÓN DE CAJA",
                font=("Arial", 18, "bold"),
                bg='#8B5CF6',
                fg='white').pack(expand=True)
        
        # Frame de estado de caja
        self.estado_frame = tk.Frame(self.parent, bg='white', relief=tk.RIDGE, bd=2)
        self.estado_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Título del estado
        tk.Label(self.estado_frame, text="Estado de la Caja", font=("Arial", 14, "bold"),
                bg='white', fg='black').pack(pady=10)
        
        # Estado actual
        self.estado_label = tk.Label(self.estado_frame, text="Caja Cerrada", 
                                     font=("Arial", 12, "bold"), bg='white', fg='red')
        self.estado_label.pack(pady=5)
        
        # Info de caja abierta
        self.info_frame = tk.Frame(self.estado_frame, bg='white')
        self.info_frame.pack(pady=10)
        
        # Botones de acción
        buttons_frame = tk.Frame(self.parent, bg='#F0F4F8')
        buttons_frame.pack(pady=10)
        
        self.btn_abrir = tk.Button(buttons_frame, text="🔓 Abrir Caja", font=('Arial', 11, 'bold'),
                                   bg='#10B981', fg='white', width=15, height=2,
                                   command=self.abrir_caja)
        self.btn_abrir.pack(side=tk.LEFT, padx=10)
        
        self.btn_cerrar = tk.Button(buttons_frame, text="🔒 Cerrar Caja", font=('Arial', 11, 'bold'),
                                    bg='#EF4444', fg='white', width=15, height=2,
                                    command=self.cerrar_caja, state=tk.DISABLED)
        self.btn_cerrar.pack(side=tk.LEFT, padx=10)
        
        tk.Button(buttons_frame, text="📊 Ver Historial", font=('Arial', 11),
                 bg='#3B82F6', fg='white', width=15, height=2,
                 command=self.ver_historial).pack(side=tk.LEFT, padx=10)
        
        # Botón eliminar solo para admin
        if self.user_data['rol'] == 'admin':
            tk.Button(buttons_frame, text="🗑️ Eliminar Caja", font=('Arial', 11),
                     bg='#DC2626', fg='white', width=15, height=2,
                     command=self.eliminar_caja).pack(side=tk.LEFT, padx=10)
        
        # Tabla de historial reciente
        tk.Label(self.parent, text="Historial Reciente", font=("Arial", 12, "bold"),
                bg='#F0F4F8', fg='black').pack(pady=(20, 5))
        
        columns = ('id', 'usuario', 'fecha_apertura', 'fecha_cierre', 'monto_inicial', 'monto_final', 'estado')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=10)
        
        self.tree.heading('id', text='ID')
        self.tree.heading('usuario', text='Usuario')
        self.tree.heading('fecha_apertura', text='Apertura')
        self.tree.heading('fecha_cierre', text='Cierre')
        self.tree.heading('monto_inicial', text='Monto Inicial')
        self.tree.heading('monto_final', text='Monto Final')
        self.tree.heading('estado', text='Estado')
        
        self.tree.column('id', width=50)
        self.tree.column('usuario', width=150)
        self.tree.column('fecha_apertura', width=130)
        self.tree.column('fecha_cierre', width=130)
        self.tree.column('monto_inicial', width=100, anchor=tk.E)
        self.tree.column('monto_final', width=100, anchor=tk.E)
        self.tree.column('estado', width=80)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar_v.set)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble click para ver detalles
        self.tree.bind('<Double-Button-1>', lambda e: self.ver_detalle_caja())
        
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
            
            # Mostrar información
            tk.Label(self.info_frame, text=f"Abierta por: {caja_abierta['usuario']}", 
                    bg='white', fg='black', font=("Arial", 10)).pack(anchor=tk.W, padx=20)
            tk.Label(self.info_frame, text=f"Fecha: {caja_abierta['fecha_apertura'][:16]}", 
                    bg='white', fg='black', font=("Arial", 10)).pack(anchor=tk.W, padx=20)
            tk.Label(self.info_frame, text=f"Monto Inicial: ${caja_abierta['monto_inicial']:.2f}", 
                    bg='white', fg='black', font=("Arial", 10, 'bold')).pack(anchor=tk.W, padx=20)
        else:
            self.estado_label.config(text="❌ Caja Cerrada", fg='#EF4444')
            self.btn_abrir.config(state=tk.NORMAL)
            self.btn_cerrar.config(state=tk.DISABLED)
            
            tk.Label(self.info_frame, text="No hay caja abierta actualmente", 
                    bg='white', fg='gray', font=("Arial", 10, 'italic')).pack(pady=10)
    
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
            DetalleCajaDialog(self.parent, caja)
    
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
                f"${caja['monto_inicial']:.2f}",
                f"${caja['monto_final']:.2f}" if caja['monto_final'] else 'N/A',
                caja['estado'].capitalize()
            ))
    
    def actualizar_todo(self):
        """Actualizar toda la vista"""
        self.actualizar_estado_caja()
        self.cargar_historial()


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
            monto = float(self.monto_entry.get().strip())
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
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Cerrar Caja")
        self.dialog.geometry("450x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centrar
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 225
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
        self.dialog.geometry(f"450x600+{x}+{y}")
        
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
        
        tk.Label(info_frame, text=f"Monto Inicial: ${self.caja_data['monto_inicial']:.2f}", 
                bg='#F3F4F6', fg='black', font=("Arial", 10, 'bold')).pack(anchor=tk.W, padx=10, pady=5)
        tk.Label(info_frame, text=f"Abierta: {self.caja_data['fecha_apertura'][:16]}", 
                bg='#F3F4F6', fg='black', font=("Arial", 9)).pack(anchor=tk.W, padx=10, pady=2)
        
        # Frame para campos con scroll
        campos_container = tk.Frame(main_frame, bg='white')
        campos_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Crear frame con scroll para los campos
        canvas = tk.Canvas(campos_container, bg='white', height=320)
        scrollbar = ttk.Scrollbar(campos_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Campos de entrada
        fields = [
            ("Ventas en Efectivo:", "ventas_efectivo"),
            ("Ventas con Tarjeta:", "ventas_tarjeta"),
            ("Reparaciones en Efectivo:", "reparaciones_efectivo"),
            ("Reparaciones con Tarjeta:", "reparaciones_tarjeta"),
            ("Otros Ingresos:", "otros_ingresos"),
            ("Otros Egresos:", "otros_egresos"),
        ]
        
        self.entries = {}
        for label, key in fields:
            tk.Label(scrollable_frame, text=label, bg='white', fg='black',
                    font=("Arial", 9)).pack(anchor=tk.W, pady=3)
            entry = tk.Entry(scrollable_frame, width=35, font=("Arial", 10))
            entry.insert(0, "0")
            entry.pack(anchor=tk.W, pady=3)
            self.entries[key] = entry
        
        # Monto final
        tk.Label(scrollable_frame, text="Monto Final en Caja:", bg='white', fg='black',
                font=("Arial", 10, 'bold')).pack(anchor=tk.W, pady=5)
        self.monto_final_entry = tk.Entry(scrollable_frame, width=35, font=("Arial", 11))
        self.monto_final_entry.pack(anchor=tk.W, pady=3)
        
        # Observaciones
        tk.Label(scrollable_frame, text="Observaciones:", bg='white', fg='black',
                font=("Arial", 9)).pack(anchor=tk.W, pady=3)
        self.obs_entry = tk.Entry(scrollable_frame, width=35, font=("Arial", 10))
        self.obs_entry.pack(anchor=tk.W, pady=3)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones (fuera del scroll, siempre visibles)
        buttons_frame = tk.Frame(main_frame, bg='white')
        buttons_frame.pack(pady=10)
        
        tk.Button(buttons_frame, text="Cerrar Caja", font=('Arial', 10), bg='#EF4444', fg='white',
                 width=12, command=self.cerrar).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons_frame, text="Cancelar", font=('Arial', 10), bg='#6B7280', fg='white',
                 width=12, command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def cerrar(self):
        """Cerrar la caja"""
        try:
            monto_final = float(self.monto_final_entry.get().strip())
            ventas_efectivo = float(self.entries['ventas_efectivo'].get().strip())
            ventas_tarjeta = float(self.entries['ventas_tarjeta'].get().strip())
            reparaciones_efectivo = float(self.entries['reparaciones_efectivo'].get().strip())
            reparaciones_tarjeta = float(self.entries['reparaciones_tarjeta'].get().strip())
            otros_ingresos = float(self.entries['otros_ingresos'].get().strip())
            otros_egresos = float(self.entries['otros_egresos'].get().strip())
        except ValueError:
            messagebox.showerror("Error", "Todos los montos deben ser números válidos")
            return
        
        observaciones = self.obs_entry.get().strip()
        
        success, mensaje = self.caja_model.cerrar_caja(
            self.caja_data['id'], monto_final, ventas_efectivo, ventas_tarjeta,
            reparaciones_efectivo, reparaciones_tarjeta, otros_ingresos, otros_egresos,
            observaciones
        )
        
        if success:
            messagebox.showinfo("Éxito", mensaje)
            self.callback()
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", mensaje)


class DetalleCajaDialog:
    def __init__(self, parent, caja_data):
        self.caja_data = caja_data
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Detalle de Caja")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        
        # Centrar
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - 250
        y = parent.winfo_y() + (parent.winfo_height() // 2) - 300
        self.dialog.geometry(f"500x600+{x}+{y}")
        
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
        
        # Datos
        datos = [
            ("Usuario:", self.caja_data['usuario']),
            ("Estado:", self.caja_data['estado'].capitalize()),
            ("Fecha Apertura:", self.caja_data['fecha_apertura'][:16] if self.caja_data['fecha_apertura'] else 'N/A'),
            ("Fecha Cierre:", self.caja_data['fecha_cierre'][:16] if self.caja_data['fecha_cierre'] else 'No cerrada'),
            ("", ""),
            ("Monto Inicial:", f"${self.caja_data['monto_inicial']:.2f}"),
            ("Ventas Efectivo:", f"${self.caja_data['ventas_efectivo']:.2f}"),
            ("Ventas Tarjeta:", f"${self.caja_data['ventas_tarjeta']:.2f}"),
            ("Reparaciones Efectivo:", f"${self.caja_data['reparaciones_efectivo']:.2f}"),
            ("Reparaciones Tarjeta:", f"${self.caja_data['reparaciones_tarjeta']:.2f}"),
            ("Otros Ingresos:", f"${self.caja_data['otros_ingresos']:.2f}"),
            ("Otros Egresos:", f"${self.caja_data['otros_egresos']:.2f}"),
            ("", ""),
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
        
        # Monto final
        if self.caja_data['monto_final'] is not None:
            tk.Frame(info_frame, bg='#E5E7EB', height=2).pack(fill=tk.X, pady=10)
            row_frame = tk.Frame(info_frame, bg='white')
            row_frame.pack(fill=tk.X, pady=5)
            tk.Label(row_frame, text="Monto Final:", bg='white', fg='black',
                    font=("Arial", 12, 'bold'), width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row_frame, text=f"${self.caja_data['monto_final']:.2f}", bg='white',
                    fg='#10B981', font=("Arial", 12, 'bold'), anchor=tk.W).pack(side=tk.LEFT)
            
            # Diferencia
            diferencia = self.caja_data['monto_final'] - self.caja_data['monto_inicial']
            color_dif = '#10B981' if diferencia >= 0 else '#EF4444'
            row_frame = tk.Frame(info_frame, bg='white')
            row_frame.pack(fill=tk.X, pady=5)
            tk.Label(row_frame, text="Diferencia:", bg='white', fg='black',
                    font=("Arial", 11, 'bold'), width=20, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row_frame, text=f"${diferencia:.2f}", bg='white',
                    fg=color_dif, font=("Arial", 11, 'bold'), anchor=tk.W).pack(side=tk.LEFT)
        
        # Observaciones
        if self.caja_data.get('observaciones'):
            tk.Label(info_frame, text="Observaciones:", bg='white', fg='black',
                    font=("Arial", 10, 'bold')).pack(anchor=tk.W, pady=(10, 5))
            tk.Label(info_frame, text=self.caja_data['observaciones'], bg='white', fg='black',
                    font=("Arial", 9), wraplength=400, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Botón cerrar
        tk.Button(main_frame, text="Cerrar", font=('Arial', 10), bg='#6B7280', fg='white',
                 width=15, command=self.dialog.destroy).pack(pady=20)


class HistorialCajasDialog:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.caja_model = Caja(db_manager)
        
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
        
        tk.Button(filter_frame, text="Filtrar", bg='#3B82F6', fg='white',
                 command=self.cargar_historial).grid(row=0, column=4, padx=5)
        tk.Button(filter_frame, text="Limpiar", bg='#6B7280', fg='white',
                 command=self.limpiar_filtros).grid(row=0, column=5, padx=5)
        
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
        
        cajas = self.caja_model.obtener_cajas(fecha_desde, fecha_hasta, limit=100)
        
        for caja in cajas:
            diferencia = ''
            if caja['monto_final'] is not None:
                dif = caja['monto_final'] - caja['monto_inicial']
                diferencia = f"${dif:.2f}"
            
            self.tree.insert('', tk.END, values=(
                caja['id'],
                caja['usuario'],
                caja['fecha_apertura'][:16] if caja['fecha_apertura'] else '',
                caja['fecha_cierre'][:16] if caja['fecha_cierre'] else 'Abierta',
                f"${caja['monto_inicial']:.2f}",
                f"${caja['monto_final']:.2f}" if caja['monto_final'] else 'N/A',
                diferencia,
                caja['estado'].capitalize()
            ))
    
    def limpiar_filtros(self):
        """Limpiar filtros"""
        self.fecha_desde.delete(0, tk.END)
        self.fecha_hasta.delete(0, tk.END)
        self.cargar_historial()
    
    def ver_detalle(self):
        """Ver detalle de caja seleccionada"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        caja_id = item['values'][0]
        
        caja = self.caja_model.obtener_caja_por_id(caja_id)
        if caja:
            DetalleCajaDialog(self.dialog, caja)

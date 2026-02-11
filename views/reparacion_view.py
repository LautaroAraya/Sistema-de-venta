import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from models.reparacion import Reparacion
from models.configuracion import Configuracion
from datetime import datetime
from PIL import Image, ImageTk
import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Circle, Line
from reportlab.graphics import renderPDF
import io


class ReparacionView:
    def agregar_foto_reparacion(self):
        """Permitir agregar fotos antes de guardar la reparación"""
        from tkinter import filedialog
        from PIL import Image
        import shutil
        import uuid
        # Abrir diálogo para seleccionar imagen
        archivo = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png"), ("Todos", "*.*")]
        )
        if not archivo:
            return
        # Carpeta temporal segura en el usuario
        import platform
        if platform.system() == "Windows":
            base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
            carpeta_temp = os.path.join(base_dir, "SistemaDeVentas", "fotos_temporales")
        else:
            carpeta_temp = os.path.join(os.path.expanduser("~"), ".sistemaventas", "fotos_temporales")
        os.makedirs(carpeta_temp, exist_ok=True)
        # Nombre único
        ext = os.path.splitext(archivo)[1].lower()
        nombre_foto = f"temp_{uuid.uuid4().hex}{ext}"
        ruta_destino = os.path.join(carpeta_temp, nombre_foto)
        # Copiar imagen
        shutil.copy(archivo, ruta_destino)
        # Guardar en lista temporal
        if not hasattr(self, 'fotos_temporales'):
            self.fotos_temporales = []
        self.fotos_temporales.append(ruta_destino)
        self.actualizar_contador_fotos_temporales()
        messagebox.showinfo("Foto agregada", "La foto se agregó temporalmente. Se guardará al registrar la reparación.")

    def actualizar_contador_fotos_temporales(self):
        if hasattr(self, 'fotos_label'):
            cantidad = len(getattr(self, 'fotos_temporales', []))
            self.fotos_label.config(text=f"Fotos: {cantidad}")

    def limpiar_fotos_temporales(self):
        import os
        if hasattr(self, 'fotos_temporales'):
            for foto in self.fotos_temporales:
                try:
                    os.remove(foto)
                except Exception:
                    pass
            self.fotos_temporales = []
            self.actualizar_contador_fotos_temporales()

    def estado_ui_to_db(self, estado_ui):
        """Convierte el estado mostrado en la UI al valor de la base de datos"""
        mapa = {
            'En Proceso': 'en_proceso',
            'En Espera de Retiro': 'en_espera_retiro',
            'Retirado': 'retirado',
        }
        return mapa.get(estado_ui, 'en_proceso')

    def estado_db_to_ui(self, estado_db):
        """Convierte el estado de la base de datos al mostrado en la UI"""
        mapa = {
            'en_proceso': 'En Proceso',
            'en_espera_retiro': 'En Espera de Retiro',
            'retirado': 'Retirado',
        }
        return mapa.get(estado_db, 'En Proceso')

    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.reparacion_model = Reparacion(db_manager)
        self.config_model = Configuracion(db_manager)
        # Variables para el formulario
        self.cliente_nombre_var = tk.StringVar()
        self.cliente_telefono_var = tk.StringVar()
        self.cliente_email_var = tk.StringVar()
        self.dispositivo_var = tk.StringVar()
        self.modelo_var = tk.StringVar()
        self.numero_serie_var = tk.StringVar()
        self.problema_var = tk.StringVar()
        self.sena_var = tk.StringVar()
        self.total_var = tk.StringVar()
        self.estado_var = tk.StringVar(value='En Proceso')
        self.observaciones_var = tk.StringVar()
        self.buscar_cliente_var = tk.StringVar()
        # Variables de estado inicial
        self.sin_bateria_var = tk.BooleanVar()
        self.rajado_var = tk.BooleanVar()
        self.mojado_var = tk.BooleanVar()
        # Variables de seguridad
        self.contrasena_var = tk.StringVar()
        self.patron_var = tk.StringVar()  # Almacenará el patrón como string
        # Variables para el canvas del patrón
        self.patron_puntos = []  # Lista de números del patrón
        self.patron_arrastrando = False
        self.patron_canvas = None
        self.patron_circulos = {}  # Diccionario de círculos dibujados
        self.patron_lineas = []  # Lista de líneas dibujadas
        # Variables de fotos
        self.fotos_actuales = []  # Lista de rutas de fotos
        self.fotos_frame = None  # Frame para mostrar miniaturas de fotos
        # Variables de control
        self.reparacion_actual = None
        self.modo_edicion = False
        self.create_widgets()
        self.cargar_reparaciones()

    def create_widgets(self):
        """Crear widgets de la interfaz"""
        # Limpiar frame
        for widget in self.parent.winfo_children():
            widget.destroy()

        self.parent.configure(bg='#F0F4F8')

        # Título
        title_frame = tk.Frame(self.parent, bg='#8B5CF6', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)

        tk.Label(title_frame,
                 text="🔧 REPARACIONES DE CELULARES",
                 font=("Arial", 18, "bold"),
                 bg='#8B5CF6',
                 fg='white').pack(expand=True)

        # Contenedor principal
        parent = tk.Frame(self.parent, bg='#F0F4F8')
        parent.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Solo la lista de comprobantes y el botón para abrir el formulario
        list_frame = tk.Frame(parent, bg='white', bd=1, relief=tk.RIDGE, padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columns = ('numero', 'cliente', 'dispositivo', 'estado', 'sena', 'total', 'fecha')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)
        headings = ['N° Orden', 'Cliente', 'Dispositivo', 'Estado', 'Seña', 'Total', 'Fecha']
        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
        self.tree.column('numero', width=90)
        self.tree.column('cliente', width=140)
        self.tree.column('dispositivo', width=120)
        self.tree.column('estado', width=90)
        self.tree.column('sena', width=80)
        self.tree.column('total', width=80)
        self.tree.column('fecha', width=90)

        yscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Botonera de acciones debajo de la tabla
        actions_frame = tk.Frame(self.parent, bg='#F0F4F8')
        actions_frame.pack(pady=(0, 10))
        btn_ver = tk.Button(actions_frame, text="👁️ Ver", font=('Arial', 11, 'bold'), bg='#3B82F6', fg='white', activebackground='#2563EB', bd=0, pady=10, cursor='hand2', command=self.ver_detalles)
        btn_ver.pack(side=tk.LEFT, padx=5, ipadx=10)
        btn_editar = tk.Button(actions_frame, text="✏️ Editar", font=('Arial', 11, 'bold'), bg='#F59E0B', fg='white', activebackground='#D97706', bd=0, pady=10, cursor='hand2', command=self.editar_reparacion)
        btn_editar.pack(side=tk.LEFT, padx=5, ipadx=10)
        btn_eliminar = tk.Button(actions_frame, text="🗑️ Eliminar", font=('Arial', 11, 'bold'), bg='#EF4444', fg='white', activebackground='#B91C1C', bd=0, pady=10, cursor='hand2', command=self.eliminar_reparacion)
        btn_eliminar.pack(side=tk.LEFT, padx=5, ipadx=10)

        self.btn_finalizar_pago = tk.Button(actions_frame, text="✅ Finalizar pago", font=('Arial', 11, 'bold'), bg='#10B981', fg='white', activebackground='#059669', bd=0, pady=10, cursor='hand2', command=self.abrir_finalizar_pago, state=tk.DISABLED)
        self.btn_finalizar_pago.pack(side=tk.LEFT, padx=5, ipadx=10)

        # Botón para abrir el formulario completo
        btn_formulario = tk.Button(actions_frame,
            text="📝 Formulario Completo",
            font=('Arial', 11, 'bold'),
            bg='#6366F1',
            fg='white',
            activebackground='#4338CA',
            bd=0,
            pady=10,
            cursor='hand2',
            command=self.abrir_formulario_completo)
        btn_formulario.pack(side=tk.LEFT, padx=5, ipadx=10)


        self.tree.bind('<<TreeviewSelect>>', self.on_reparacion_select)
        self.actualizar_estado_finalizar_pago()

        # (El botón para abrir el formulario completo ya está en la botonera de acciones)

    def abrir_formulario_completo(self):
        # Ventana modal para el formulario completo
        top = tk.Toplevel(self.parent)
        top.title("Formulario Completo de Reparación")
        top.grab_set()
        top.geometry("900x700")
        top.configure(bg='#F0F4F8')
        self.form_window = top

        def _cerrar_formulario():
            try:
                top.grab_release()
            except tk.TclError:
                pass
            self.form_window = None
            top.destroy()

        top.protocol("WM_DELETE_WINDOW", _cerrar_formulario)

        # Canvas con scrollbar para el formulario
        canvas = tk.Canvas(top, bg='#F0F4F8')
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=vsb.set)

        form_frame = tk.Frame(canvas, bg='white', bd=1, relief=tk.RIDGE, padx=20, pady=20)
        canvas.create_window((0, 0), window=form_frame, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        form_frame.bind("<Configure>", _on_configure)

        # Cliente y contacto
        tk.Label(form_frame, text="Cliente:", font=("Arial", 10, "bold"), bg='white').grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.cliente_nombre_var, font=("Arial", 10), width=30).grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Teléfono:", font=("Arial", 10, "bold"), bg='white').grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.cliente_telefono_var, font=("Arial", 10), width=20).grid(row=0, column=3, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Email:", font=("Arial", 10, "bold"), bg='white').grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.cliente_email_var, font=("Arial", 10), width=30).grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)

        # Equipo
        tk.Label(form_frame, text="Dispositivo:", font=("Arial", 10, "bold"), bg='white').grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.dispositivo_var, font=("Arial", 10), width=30).grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Modelo:", font=("Arial", 10, "bold"), bg='white').grid(row=2, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.modelo_var, font=("Arial", 10), width=20).grid(row=2, column=3, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="DNI:", font=("Arial", 10, "bold"), bg='white').grid(row=3, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.numero_serie_var, font=("Arial", 10), width=30).grid(row=3, column=1, sticky=tk.EW, pady=5, padx=5)

        # Problema
        tk.Label(form_frame, text="Problema:", font=("Arial", 10, "bold"), bg='white').grid(row=4, column=0, sticky=tk.NW, pady=5, padx=5)
        problema_text = tk.Text(form_frame, font=("Arial", 10), height=4, width=50)
        problema_text.grid(row=4, column=1, columnspan=3, sticky=tk.NSEW, pady=5, padx=5)
        self.problema_text = problema_text

        # Estado Inicial (checkboxes)
        tk.Label(form_frame, text="Estado Inicial:", font=("Arial", 10, "bold"), bg='white').grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        estado_inicial_frame = tk.Frame(form_frame, bg='white')
        estado_inicial_frame.grid(row=5, column=1, columnspan=3, sticky=tk.W, pady=5, padx=5)
        self.chk_sin_bateria = tk.Checkbutton(estado_inicial_frame, text="Sin Batería", variable=self.sin_bateria_var, bg='white', font=("Arial", 10))
        self.chk_sin_bateria.pack(side=tk.LEFT, padx=5)
        self.chk_rajado = tk.Checkbutton(estado_inicial_frame, text="Rajado", variable=self.rajado_var, bg='white', font=("Arial", 10))
        self.chk_rajado.pack(side=tk.LEFT, padx=5)
        self.chk_mojado = tk.Checkbutton(estado_inicial_frame, text="Mojado", variable=self.mojado_var, bg='white', font=("Arial", 10))
        self.chk_mojado.pack(side=tk.LEFT, padx=5)


           # Patrón y contraseña (fila 6 col 0-1)
        tk.Label(form_frame, text="Patrón:", font=("Arial", 10, "bold"), bg='white').grid(row=6, column=0, sticky=tk.NW, pady=10, padx=5)
        patron_frame = tk.Frame(form_frame, bg='white')
        patron_frame.grid(row=6, column=1, sticky=tk.W, pady=10, padx=5)
           # Canvas para dibujar el patrón
        self.patron_canvas = tk.Canvas(patron_frame, width=150, height=150, bg='white', relief=tk.RIDGE, bd=1)
        self.patron_canvas.pack(side=tk.LEFT, padx=(0, 10))
        # Inicializar el canvas del patrón
        self.inicializar_patron_canvas()
           # Frame para botón y label del patrón
        patron_controls = tk.Frame(patron_frame, bg='white')
        patron_controls.pack(side=tk.LEFT, fill=tk.Y)
           # Botón para limpiar el patrón
        tk.Button(patron_controls, text="🔄 Limpiar", font=("Arial", 8), 
                  bg='#F59E0B', fg='white', command=self.limpiar_patron, 
                  width=10).pack(pady=5)
           # Label para mostrar el patrón actual
        self.patron_label = tk.Label(patron_controls, text="", font=("Arial", 8), bg='white', fg='gray', wraplength=100)
        self.patron_label.pack(pady=5)

           # Campo contraseña debajo del patrón
        tk.Label(form_frame, text="Contraseña:", font=("Arial", 10, "bold"), bg='white').grid(row=7, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.contrasena_var, font=("Arial", 10), width=30).grid(row=7, column=1, sticky=tk.EW, pady=5, padx=5)

           # Fila 7 col 2-3: Seña y Total
        tk.Label(form_frame, text="Seña ($):", font=("Arial", 10, "bold"), bg='white').grid(row=8, column=2, sticky=tk.W, pady=10, padx=5)
        ttk.Entry(form_frame, textvariable=self.sena_var, font=("Arial", 10), width=20).grid(row=8, column=3, sticky=tk.EW, pady=10, padx=5)

        tk.Label(form_frame, text="Total ($):", font=("Arial", 10, "bold"), bg='white').grid(row=9, column=2, sticky=tk.W, pady=10, padx=5)
        ttk.Entry(form_frame, textvariable=self.total_var, font=("Arial", 10), width=20).grid(row=9, column=3, sticky=tk.EW, pady=10, padx=5)

           # Fila 9: Estado
        tk.Label(form_frame, text="Estado:", font=("Arial", 10, "bold"), bg='white').grid(row=9, column=0, sticky=tk.W, pady=10, padx=5)
        estado_combo = ttk.Combobox(form_frame, textvariable=self.estado_var, 
                       values=['En Proceso', 'En Espera de Retiro', 'Retirado'],
                       font=("Arial", 10), width=18)
        estado_combo.grid(row=9, column=1, sticky=tk.EW, pady=10, padx=5)

           # Fila 10: Observaciones
        tk.Label(form_frame, text="Observaciones:", font=("Arial", 10, "bold"), bg='white').grid(row=10, column=0, sticky=tk.NW, pady=10, padx=5)
        obs_text = tk.Text(form_frame, font=("Arial", 10), height=3, width=50)
        obs_text.grid(row=10, column=1, columnspan=3, sticky=tk.NSEW, pady=10, padx=5)
        self.observaciones_text = obs_text

        # Fila 11: Fotos
        tk.Label(form_frame, text="Fotos:", font=("Arial", 10, "bold"), bg='white').grid(row=11, column=0, sticky=tk.NW, pady=10, padx=5)
        fotos_controls = tk.Frame(form_frame, bg='white')
        fotos_controls.grid(row=11, column=1, columnspan=3, sticky=tk.EW, pady=10, padx=5)
        tk.Button(fotos_controls, text="📷 Agregar Foto", font=("Arial", 10), 
             command=self.agregar_foto_reparacion).pack(side=tk.LEFT, padx=5)
        tk.Button(fotos_controls, text="🖼️ Ver Galería", font=("Arial", 10), 
             command=self.ver_galeria_fotos).pack(side=tk.LEFT, padx=5)
        tk.Button(fotos_controls, text="🗑️ Eliminar Todas", font=("Arial", 10), 
             command=self.eliminar_todas_fotos).pack(side=tk.LEFT, padx=5)
        # Mostrar cantidad de fotos
        self.fotos_label = tk.Label(fotos_controls, text="Fotos: 0", font=("Arial", 9), fg='gray', bg='white')
        self.fotos_label.pack(side=tk.LEFT, padx=10)

        # Botonera principal dentro del formulario, bien separada (solo una vez)
        button_frame = tk.Frame(form_frame, bg='#F0F4F8')
        button_frame.grid(row=12, column=0, columnspan=4, sticky=tk.EW, pady=25, padx=20)

        self.btn_guardar = tk.Button(button_frame,
                              text="💾 Guardar Reparación",
                              font=('Arial', 11, 'bold'),
                              bg='#10B981',
                              fg='white',
                              activebackground='#059669',
                              bd=0,
                              pady=10,
                              cursor='hand2',
                              command=self.guardar_reparacion)
        self.btn_guardar.pack(side=tk.LEFT, padx=5, ipadx=20)

        tk.Button(button_frame,
            text="🖨️ Imprimir boleta",
            font=('Arial', 11, 'bold'),
            bg='#3B82F6',
            fg='white',
            activebackground='#2563EB',
            bd=0,
            pady=10,
            cursor='hand2',
            command=self.imprimir_boleta).pack(side=tk.LEFT, padx=5, ipadx=20)

        tk.Button(button_frame,
            text="🔄 Limpiar",
            font=('Arial', 11, 'bold'),
            bg='#F59E0B',
            fg='white',
            activebackground='#D97706',
            bd=0,
            pady=10,
            cursor='hand2',
            command=self.limpiar_formulario).pack(side=tk.LEFT, padx=5, ipadx=20)

        # Configurar expansión de columnas
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(3, weight=1)

    def inicializar_patron_canvas(self):
        """Inicializar el canvas del patrón con círculos interactivos"""
        if not self.patron_canvas:
            return
        
        # Limpiar canvas
        self.patron_canvas.delete("all")
        self.patron_circulos = {}
        
        # Posiciones de los círculos en la cuadrícula 3x3
        spacing = 50
        offset = 25
        
        for num in range(1, 10):
            row = (num - 1) // 3
            col = (num - 1) % 3
            x = offset + col * spacing
            y = offset + row * spacing
            
            # Dibujar círculo
            circulo = self.patron_canvas.create_oval(x-10, y-10, x+10, y+10, 
                                                     fill='white', outline='black', width=2,
                                                     tags=f'punto_{num}')
            
            # Dibujar número dentro del círculo
            self.patron_canvas.create_text(x, y, text=str(num), font=("Arial", 10, "bold"),
                                          tags=f'texto_{num}')
            
            self.patron_circulos[num] = {'x': x, 'y': y, 'circulo': circulo}
        
        # Eventos del mouse
        self.patron_canvas.bind("<Button-1>", self.patron_mouse_down)
        self.patron_canvas.bind("<B1-Motion>", self.patron_mouse_drag)
        self.patron_canvas.bind("<ButtonRelease-1>", self.patron_mouse_up)
    
    def patron_mouse_down(self, event):
        """Iniciar dibujo del patrón"""
        self.patron_arrastrando = True
        num = self.obtener_punto_cercano(event.x, event.y)
        if num and num not in self.patron_puntos:
            self.patron_puntos.append(num)
            self.actualizar_patron_visual()
    
    def patron_mouse_drag(self, event):
        """Continuar dibujando el patrón mientras se arrastra"""
        if not self.patron_arrastrando:
            return
        
        num = self.obtener_punto_cercano(event.x, event.y)
        if num and num not in self.patron_puntos:
            self.patron_puntos.append(num)
            self.actualizar_patron_visual()
    
    def patron_mouse_up(self, event):
        """Finalizar dibujo del patrón"""
        self.patron_arrastrando = False
        # Guardar el patrón en formato string
        if self.patron_puntos:
            self.patron_var.set('-'.join(map(str, self.patron_puntos)))
            self.patron_label.config(text=f"Patrón: {self.patron_var.get()}")
    
    def obtener_punto_cercano(self, x, y):
        """Obtener el número del punto más cercano al cursor"""
        for num, data in self.patron_circulos.items():
            dx = data['x'] - x
            dy = data['y'] - y
            distancia = (dx**2 + dy**2) ** 0.5
            if distancia <= 15:  # Radio de detección
                return num
        return None
    
    def actualizar_patron_visual(self):
        """Actualizar la visualización del patrón en el canvas"""
        # Limpiar líneas anteriores
        for linea in self.patron_lineas:
            self.patron_canvas.delete(linea)
        self.patron_lineas = []
        
        # Restaurar todos los círculos a su estado original
        for num, data in self.patron_circulos.items():
            self.patron_canvas.itemconfig(data['circulo'], fill='white', outline='black', width=2)
        
        # Resaltar los círculos seleccionados
        for num in self.patron_puntos:
            if num in self.patron_circulos:
                self.patron_canvas.itemconfig(self.patron_circulos[num]['circulo'], 
                                             fill='#3B82F6', outline='#1D4ED8', width=3)
        
        # Dibujar líneas conectando los puntos
        for i in range(len(self.patron_puntos) - 1):
            num1 = self.patron_puntos[i]
            num2 = self.patron_puntos[i + 1]
            
            if num1 in self.patron_circulos and num2 in self.patron_circulos:
                x1 = self.patron_circulos[num1]['x']
                y1 = self.patron_circulos[num1]['y']
                x2 = self.patron_circulos[num2]['x']
                y2 = self.patron_circulos[num2]['y']
                
                linea = self.patron_canvas.create_line(x1, y1, x2, y2, 
                                                       fill='#3B82F6', width=3)
                self.patron_lineas.append(linea)
                # Enviar líneas al fondo para que los círculos queden arriba
                self.patron_canvas.tag_lower(linea)
    
    def limpiar_patron(self):
        """Limpiar el patrón dibujado"""
        self.patron_puntos = []
        self.patron_var.set('')
        self.patron_label.config(text='')
        self.actualizar_patron_visual()
    
    def cargar_reparaciones(self):
        """Cargar lista de reparaciones en la tabla"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener reparaciones
        reparaciones = self.reparacion_model.obtener_reparaciones()
        
        # Agregar filas
        for rep in reparaciones:
            fecha = rep['fecha_creacion'].split(' ')[0] if rep['fecha_creacion'] else 'N/A'
            sena = f"${int(rep['sena'])}" if rep['sena'] else "$0"
            total = f"${int(rep['total'])}" if rep['total'] else "$0"
            self.tree.insert('', 'end', 
                           values=(rep['numero_orden'], rep['cliente_nombre'], 
                                  rep['dispositivo'], rep['estado'],
                                  sena, total, fecha))

    # Eliminada la función on_tree_action_click porque ya no hay columna de acción
    
    def filtrar_reparaciones(self, estado):
        """Filtrar reparaciones por estado"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if estado == 'Todas':
            reparaciones = self.reparacion_model.obtener_reparaciones()
        else:
            reparaciones = self.reparacion_model.obtener_reparaciones(estado)
        
        # Agregar filas
        for rep in reparaciones:
            fecha = rep['fecha_creacion'].split(' ')[0] if rep['fecha_creacion'] else 'N/A'
            sena = f"${rep['sena']:.2f}" if rep['sena'] else "$0.00"
            total = f"${rep['total']:.2f}" if rep['total'] else "$0.00"
            
            self.tree.insert('', 'end', 
                           values=(rep['numero_orden'], rep['cliente_nombre'], 
                                  rep['dispositivo'], rep['estado'],
                                  sena, total, fecha, 'Ver'))
    
    def ver_detalles(self):
        """Ver detalles de una reparación"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona una reparación")
            return
        
        # Obtener número de orden
        item = self.tree.item(seleccion[0])
        numero_orden = item['values'][0]
        
        # Buscar reparación
        reparaciones = self.reparacion_model.obtener_reparaciones()
        for rep in reparaciones:
            if rep['numero_orden'] == numero_orden:
                self.mostrar_detalles(rep)
                break

    def abrir_finalizar_pago(self):
        """Abrir formulario para finalizar el pago de una reparación"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona una reparación")
            return

        item = self.tree.item(seleccion[0])
        numero_orden = item['values'][0]
        reparaciones = self.reparacion_model.obtener_reparaciones()
        reparacion = None
        for rep in reparaciones:
            if rep['numero_orden'] == numero_orden:
                reparacion = rep
                break

        if not reparacion:
            messagebox.showerror("Error", "No se encontró la reparación seleccionada")
            return

        pago_final = float(reparacion.get('monto_pago_final') or 0)
        fecha_pago = reparacion.get('fecha_pago_final')
        if pago_final > 0 or fecha_pago or reparacion.get('estado') == 'retirado':
            messagebox.showinfo("Información", "El pago final ya fue registrado para esta reparación")
            self.actualizar_estado_finalizar_pago()
            return

        sena = float(reparacion.get('sena') or 0)
        total = float(reparacion.get('total') or 0)
        saldo = total - sena

        top = tk.Toplevel(self.parent)
        top.title("Finalizar pago")
        top.grab_set()
        top.geometry("420x360")
        top.configure(bg='white')

        contenido = tk.Frame(top, bg='white')
        contenido.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        tk.Label(contenido, text="Seña:", font=("Arial", 10, "bold"), bg='white').grid(row=0, column=0, sticky=tk.W, pady=6)
        tk.Label(contenido, text=f"${sena:.2f}", font=("Arial", 10), bg='white').grid(row=0, column=1, sticky=tk.W, pady=6)

        tk.Label(contenido, text="Total:", font=("Arial", 10, "bold"), bg='white').grid(row=1, column=0, sticky=tk.W, pady=6)
        tk.Label(contenido, text=f"${total:.2f}", font=("Arial", 10), bg='white').grid(row=1, column=1, sticky=tk.W, pady=6)

        tk.Label(contenido, text="Saldo:", font=("Arial", 10, "bold"), bg='white').grid(row=2, column=0, sticky=tk.W, pady=6)
        tk.Label(contenido, text=f"${saldo:.2f}", font=("Arial", 10), bg='white').grid(row=2, column=1, sticky=tk.W, pady=6)

        fecha_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        monto_var = tk.StringVar(value=f"{saldo:.2f}")
        medio_var = tk.StringVar(value='Efectivo')
        recargo_var = tk.StringVar(value='0')

        tk.Label(contenido, text="Fecha fin de pago:", font=("Arial", 10, "bold"), bg='white').grid(row=3, column=0, sticky=tk.W, pady=6)
        ttk.Entry(contenido, textvariable=fecha_var, font=("Arial", 10), width=18).grid(row=3, column=1, sticky=tk.W, pady=6)

        tk.Label(contenido, text="Monto pagado:", font=("Arial", 10, "bold"), bg='white').grid(row=4, column=0, sticky=tk.W, pady=6)
        ttk.Entry(contenido, textvariable=monto_var, font=("Arial", 10), width=18).grid(row=4, column=1, sticky=tk.W, pady=6)

        tk.Label(contenido, text="Medio:", font=("Arial", 10, "bold"), bg='white').grid(row=5, column=0, sticky=tk.W, pady=6)
        medio_combo = ttk.Combobox(contenido, textvariable=medio_var, values=['Efectivo', 'Transferencia', 'Tarjeta'], state='readonly', width=16)
        medio_combo.grid(row=5, column=1, sticky=tk.W, pady=6)

        recargo_label = tk.Label(contenido, text="Recargo %:", font=("Arial", 10, "bold"), bg='white')
        recargo_entry = ttk.Entry(contenido, textvariable=recargo_var, font=("Arial", 10), width=18)
        recargo_label.grid(row=6, column=0, sticky=tk.W, pady=6)
        recargo_entry.grid(row=6, column=1, sticky=tk.W, pady=6)

        def _guardar_pago():
            fecha_txt = fecha_var.get().strip()
            if not fecha_txt:
                messagebox.showwarning("Validación", "La fecha de pago es obligatoria")
                return
            try:
                datetime.strptime(fecha_txt, '%Y-%m-%d')
            except Exception:
                messagebox.showwarning("Validación", "La fecha debe tener formato YYYY-MM-DD")
                return
            try:
                monto = float(monto_var.get() or 0)
                recargo_pct = float(recargo_var.get() or 0)
            except Exception:
                messagebox.showwarning("Validación", "El monto y recargo deben ser números")
                return
            if monto < 0 or recargo_pct < 0:
                messagebox.showwarning("Validación", "El monto y recargo no pueden ser negativos")
                return

            recargo_monto = (monto * recargo_pct / 100)
            total_pagado = monto + recargo_monto
            medio_db = medio_var.get().lower()

            success, msg = self.reparacion_model.actualizar_reparacion(
                reparacion['id'],
                fecha_pago_final=fecha_txt,
                medio_pago_final=medio_db,
                monto_pago_final=total_pagado,
                recargo_tarjeta=recargo_monto,
                estado='retirado'
            )
            if success:
                messagebox.showinfo("Éxito", "Pago final registrado correctamente")
                top.destroy()
                self.cargar_reparaciones()
                self.actualizar_estado_finalizar_pago()
            else:
                messagebox.showerror("Error", msg)

        botones = tk.Frame(contenido, bg='white')
        botones.grid(row=7, column=0, columnspan=2, pady=15)
        tk.Button(botones, text="Guardar", font=("Arial", 10, "bold"), bg='#10B981', fg='white', bd=0, padx=15, pady=6, command=_guardar_pago).pack(side=tk.LEFT, padx=5)
        tk.Button(botones, text="Cancelar", font=("Arial", 10, "bold"), bg='#9CA3AF', fg='white', bd=0, padx=15, pady=6, command=top.destroy).pack(side=tk.LEFT, padx=5)

    def on_reparacion_select(self, _event=None):
        self.actualizar_estado_finalizar_pago()

    def actualizar_estado_finalizar_pago(self):
        if not hasattr(self, 'btn_finalizar_pago'):
            return

        seleccion = self.tree.selection()
        if not seleccion:
            self.btn_finalizar_pago.config(state=tk.DISABLED)
            return

        item = self.tree.item(seleccion[0])
        numero_orden = item['values'][0]
        reparaciones = self.reparacion_model.obtener_reparaciones()
        reparacion = None
        for rep in reparaciones:
            if rep['numero_orden'] == numero_orden:
                reparacion = rep
                break

        if not reparacion:
            self.btn_finalizar_pago.config(state=tk.DISABLED)
            return

        pago_final = float(reparacion.get('monto_pago_final') or 0)
        fecha_pago = reparacion.get('fecha_pago_final')
        estado = reparacion.get('estado')
        if pago_final > 0 or fecha_pago or estado == 'retirado':
            self.btn_finalizar_pago.config(state=tk.DISABLED)
        else:
            self.btn_finalizar_pago.config(state=tk.NORMAL)
    
    def ver_fotos(self):
        """Abrir la galería de fotos de la reparación seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona una reparación")
            return
        
        item = self.tree.item(seleccion[0])
        numero_orden = item['values'][0]
        reparaciones = self.reparacion_model.obtener_reparaciones()
        for rep in reparaciones:
            if rep['numero_orden'] == numero_orden:
                self.reparacion_actual = rep
                self.cargar_fotos_reparacion(rep['id'])
                self.ver_galeria_fotos()
                return
        messagebox.showerror("Error", "No se encontró la reparación seleccionada")
    
    def mostrar_detalles(self, reparacion):
        """Mostrar ventana con detalles de la reparación"""
        ventana = tk.Toplevel(self.parent)
        ventana.title(f"Detalles - {reparacion['numero_orden']}")
        ventana.geometry("600x600")
        ventana.configure(bg='white')
        
        # Frame de contenido
        content = tk.Frame(ventana, bg='white')
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        info = [
            ("Número de Orden:", reparacion['numero_orden']),
            ("Cliente:", reparacion['cliente_nombre']),
            ("Teléfono:", reparacion['cliente_telefono'] or 'N/A'),
            ("Email:", reparacion['cliente_email'] or 'N/A'),
            ("Dispositivo:", reparacion['dispositivo']),
            ("Modelo:", reparacion['modelo'] or 'N/A'),
            ("Nº Serie:", reparacion['numero_serie'] or 'N/A'),
            ("Estado:", reparacion['estado'].replace('_', ' ').title()),
            ("Seña:", f"${reparacion['sena']:.2f}"),
            ("Total:", f"${reparacion['total']:.2f}"),
            ("Fecha Creación:", reparacion['fecha_creacion'] or 'N/A'),
            ("Fecha Entrega:", reparacion['fecha_entrega'] or 'Pendiente'),
        ]
        
        row = 0
        for label, valor in info:
            tk.Label(content, text=label, font=("Arial", 10, "bold"), bg='white', fg='#374151').grid(row=row, column=0, sticky=tk.W, pady=8, padx=10)
            tk.Label(content, text=str(valor), font=("Arial", 10), bg='white', fg='#1F2937').grid(row=row, column=1, sticky=tk.W, pady=8, padx=10)
            row += 1
        
        # Problema
        tk.Label(content, text="Problema:", font=("Arial", 10, "bold"), bg='white', fg='#374151').grid(row=row, column=0, sticky=tk.NW, pady=8, padx=10)
        problema_text = tk.Text(content, font=("Arial", 9), height=3, width=50, bg='#F9FAFB', relief=tk.RIDGE, bd=1)
        problema_text.grid(row=row, column=1, sticky=tk.NSEW, pady=8, padx=10)
        problema_text.insert(1.0, reparacion['problema'] or '')
        problema_text.config(state=tk.DISABLED)
        row += 1
        
        # Observaciones
        tk.Label(content, text="Observaciones:", font=("Arial", 10, "bold"), bg='white', fg='#374151').grid(row=row, column=0, sticky=tk.NW, pady=8, padx=10)
        obs_text = tk.Text(content, font=("Arial", 9), height=3, width=50, bg='#F9FAFB', relief=tk.RIDGE, bd=1)
        obs_text.grid(row=row, column=1, sticky=tk.NSEW, pady=8, padx=10)
        obs_text.insert(1.0, reparacion['observaciones'] or '')
        obs_text.config(state=tk.DISABLED)
    
    def editar_reparacion(self):
        """Editar reparación seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona una reparación")
            return

        # Obtener número de orden
        item = self.tree.item(seleccion[0])
        numero_orden = item['values'][0]

        # Buscar reparación
        reparaciones = self.reparacion_model.obtener_reparaciones()
        for rep in reparaciones:
            if rep['numero_orden'] == numero_orden:
                self.reparacion_actual = rep
                self.modo_edicion = True
                # Abrir el formulario completo antes de cargar los datos
                self.abrir_formulario_completo()
                # Cargar los datos en el formulario (widgets ya existen)
                self.cargar_datos_en_formulario(rep)
                # Cambiar el texto del botón guardar
                self.btn_guardar.config(text="💾 Actualizar Reparación")
                break
    
    def cargar_datos_en_formulario(self, reparacion):
        """Cargar datos de reparación en el formulario"""
        self.cliente_nombre_var.set(reparacion['cliente_nombre'])
        self.cliente_telefono_var.set(reparacion['cliente_telefono'] or '')
        self.cliente_email_var.set(reparacion['cliente_email'] or '')
        self.dispositivo_var.set(reparacion['dispositivo'])
        self.modelo_var.set(reparacion['modelo'] or '')
        self.numero_serie_var.set(reparacion['numero_serie'] or '')
        self.sena_var.set(str(reparacion['sena']) if reparacion['sena'] else '0')
        self.total_var.set(str(reparacion['total']))
        self.estado_var.set(self.estado_db_to_ui(reparacion['estado']))
        
        # Estado inicial
        self.sin_bateria_var.set(bool(reparacion.get('sin_bateria', 0)))
        self.rajado_var.set(bool(reparacion.get('rajado', 0)))
        self.mojado_var.set(bool(reparacion.get('mojado', 0)))
        
        # Seguridad
        self.contrasena_var.set(reparacion.get('contrasena', ''))
        patron_str = reparacion.get('patron', '')
        self.patron_var.set(patron_str)
        
        # Cargar patrón en el canvas
        if patron_str:
            try:
                self.patron_puntos = [int(n.strip()) for n in patron_str.replace(',', '-').split('-') if n.strip().isdigit()]
                self.actualizar_patron_visual()
                self.patron_label.config(text=f"Patrón: {patron_str}")
            except:
                pass
        else:
            # Si no hay patrón, limpiar el canvas
            self.limpiar_patron()
        
        self.problema_text.delete(1.0, tk.END)
        self.problema_text.insert(1.0, reparacion['problema'])
        
        self.observaciones_text.delete(1.0, tk.END)
        self.observaciones_text.insert(1.0, reparacion['observaciones'] or '')
        
        # Cargar fotos de la reparación
        self.cargar_fotos_reparacion(reparacion['id'])
    
    def guardar_reparacion(self):
        """Guardar nueva reparación o actualizar existente"""
        # Validar campos obligatorios
        if not self.cliente_nombre_var.get().strip():
            messagebox.showwarning("Validación", "El nombre del cliente es obligatorio")
            return

        if not self.dispositivo_var.get().strip():
            messagebox.showwarning("Validación", "El dispositivo es obligatorio")
            return

        if not self.problema_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Validación", "La descripción del problema es obligatoria")
            return

        try:
            sena = float(self.sena_var.get() or 0)
            total = float(self.total_var.get() or 0)
        except:
            messagebox.showwarning("Validación", "La seña y total deben ser números")
            return

        if total <= 0:
            messagebox.showwarning("Validación", "El total debe ser mayor a 0")
            return

        if self.modo_edicion:
            # Actualizar reparación
            success, msg = self.reparacion_model.actualizar_reparacion(
                self.reparacion_actual['id'],
                cliente_nombre=self.cliente_nombre_var.get(),
                cliente_telefono=self.cliente_telefono_var.get(),
                cliente_email=self.cliente_email_var.get(),
                dispositivo=self.dispositivo_var.get(),
                modelo=self.modelo_var.get(),
                numero_serie=self.numero_serie_var.get() or None,
                problema=self.problema_text.get(1.0, tk.END),
                sena=sena,
                total=total,
                estado=self.estado_ui_to_db(self.estado_var.get()),
                observaciones=self.observaciones_text.get(1.0, tk.END).strip(),
                sin_bateria=self.sin_bateria_var.get(),
                rajado=self.rajado_var.get(),
                mojado=self.mojado_var.get(),
                contrasena=self.contrasena_var.get().strip(),
                patron=self.patron_var.get().strip()
            )

            if success:
                # Mover fotos temporales a la carpeta definitiva (igual que en alta)
                import shutil
                numero_orden = self.reparacion_actual['numero_orden']
                if hasattr(self, 'fotos_temporales') and self.fotos_temporales:
                    carpeta_destino = os.path.join(self.db_manager.fotos_path, f"ticket_{numero_orden}")
                    os.makedirs(carpeta_destino, exist_ok=True)
                    for i, foto_temp in enumerate(self.fotos_temporales, 1):
                        ext = os.path.splitext(foto_temp)[1].lower()
                        nombre_final = f"foto_{i:02d}{ext}"
                        shutil.move(foto_temp, os.path.join(carpeta_destino, nombre_final))
                    self.fotos_temporales = []
                    self.actualizar_contador_fotos_temporales()
                messagebox.showinfo("Éxito", "Reparación actualizada correctamente")
                self.limpiar_formulario()
                self.reparacion_actual = None  # Limpiar referencia después de editar
                self.cargar_reparaciones()
            else:
                messagebox.showerror("Error", msg)
        else:
            # Crear nueva reparación
            success, numero_orden = self.reparacion_model.agregar_reparacion(
                usuario_id=self.user_data['id'],
                cliente_nombre=self.cliente_nombre_var.get(),
                cliente_telefono=self.cliente_telefono_var.get(),
                cliente_email=self.cliente_email_var.get(),
                dispositivo=self.dispositivo_var.get(),
                modelo=self.modelo_var.get(),
                numero_serie=self.numero_serie_var.get() or None,
                problema=self.problema_text.get(1.0, tk.END),
                sena=sena,
                total=total,
                estado=self.estado_ui_to_db(self.estado_var.get()),
                observaciones=self.observaciones_text.get(1.0, tk.END).strip(),
                sin_bateria=self.sin_bateria_var.get(),
                rajado=self.rajado_var.get(),
                mojado=self.mojado_var.get(),
                contrasena=self.contrasena_var.get().strip(),
                patron=self.patron_var.get().strip()
            )
            if success:
                # Mover fotos temporales a la carpeta definitiva
                import shutil
                reparaciones = self.reparacion_model.obtener_reparaciones()
                nueva_rep = None
                for rep in reparaciones:
                    if str(rep.get('numero_orden')) == str(numero_orden):
                        nueva_rep = rep
                        break
                if nueva_rep and hasattr(self, 'fotos_temporales') and self.fotos_temporales:
                    carpeta_destino = os.path.join(self.db_manager.fotos_path, f"ticket_{numero_orden}")
                    os.makedirs(carpeta_destino, exist_ok=True)
                    for i, foto_temp in enumerate(self.fotos_temporales, 1):
                        ext = os.path.splitext(foto_temp)[1].lower()
                        nombre_final = f"foto_{i:02d}{ext}"
                        shutil.move(foto_temp, os.path.join(carpeta_destino, nombre_final))
                    self.fotos_temporales = []
                    self.actualizar_contador_fotos_temporales()
                messagebox.showinfo("Éxito", f"Reparación registrada con número: {numero_orden}")
                self.limpiar_formulario()
                self.cargar_reparaciones()
            else:
                messagebox.showerror("Error", numero_orden)
    
    def limpiar_formulario(self):
        """Limpiar formulario"""
        self.cliente_nombre_var.set('')
        self.cliente_telefono_var.set('')
        self.cliente_email_var.set('')
        self.dispositivo_var.set('')
        self.modelo_var.set('')
        self.numero_serie_var.set('')
        self.sena_var.set('')
        self.total_var.set('')
        self.estado_var.set('Pendiente')
        
        # Limpiar estado inicial
        self.sin_bateria_var.set(False)
        self.rajado_var.set(False)
        self.mojado_var.set(False)
        
        # Limpiar seguridad
        self.contrasena_var.set('')
        self.limpiar_patron()
        
        self.problema_text.delete(1.0, tk.END)
        self.observaciones_text.delete(1.0, tk.END)
        
        # Limpiar fotos
        self.fotos_actuales = []
        self.actualizar_contador_fotos()
        self.limpiar_fotos_temporales()
        # Solo limpiar self.reparacion_actual si se está editando o eliminando, no tras crear
        if self.modo_edicion:
            self.reparacion_actual = None
        self.modo_edicion = False
        self.btn_guardar.config(text="💾 Guardar Reparación")
    
    def eliminar_reparacion(self):
        """Eliminar reparación seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor selecciona una reparación")
            return

        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar esta reparación?"):
            item = self.tree.item(seleccion[0])
            numero_orden = item['values'][0]

            reparaciones = self.reparacion_model.obtener_reparaciones()
            for rep in reparaciones:
                if rep['numero_orden'] == numero_orden:
                    success, msg = self.reparacion_model.eliminar_reparacion(rep['id'])
                    if success:
                        messagebox.showinfo("Éxito", msg)
                        self.reparacion_actual = None  # Limpiar referencia después de eliminar
                        self.cargar_reparaciones()
                    else:
                        messagebox.showerror("Error", msg)
                    break
    
    def imprimir_boleta(self):
        """Generar e imprimir boleta de reparación"""
        rep = None
        # Si hay reparación cargada en el formulario, usarla
        if self.reparacion_actual:
            rep = self.reparacion_actual
        else:
            # Caso general: usar selección de la tabla
            seleccion = self.tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor selecciona una reparación")
                return
            item = self.tree.item(seleccion[0])
            numero_orden = item['values'][0]
            reparaciones = self.reparacion_model.obtener_reparaciones()
            for r in reparaciones:
                if r['numero_orden'] == numero_orden:
                    rep = r
                    break
        
        if not rep:

            self.actualizar_estado_finalizar_pago()
            messagebox.showerror("Error", "No se encontró la reparación seleccionada")
            return
        
        self.generar_boleta_pdf(rep, auto_print=True)
    
    def crear_patron_grid(self, patron_str):
        """Crear cuadrícula visual 3x3 para el patrón de desbloqueo"""
        # Crear dibujo más pequeño: 100x100 puntos
        d = Drawing(100, 100)
        
        # Posiciones de los círculos en la cuadrícula 3x3
        positions = []
        spacing = 33
        offset = 17
        
        for row in range(3):
            for col in range(3):
                x = offset + col * spacing
                y = 83 - row * spacing  # Invertir Y para que 1 esté arriba a la izquierda
                positions.append((x, y))
        
        # Dibujar todos los círculos
        for i, (x, y) in enumerate(positions):
            circle = Circle(x, y, 6)
            circle.fillColor = colors.white
            circle.strokeColor = colors.black
            circle.strokeWidth = 1.5
            d.add(circle)
        
        # Si hay un patrón, resaltar los círculos y dibujar líneas
        if patron_str:
            try:
                # Parsear el patrón (ej: "1-2-3-5-9" o "1,2,3,5,9")
                patron_numeros = [int(n.strip()) for n in patron_str.replace(',', '-').split('-') if n.strip().isdigit()]
                
                # Resaltar círculos en el patrón
                for num in patron_numeros:
                    if 1 <= num <= 9:
                        idx = num - 1
                        x, y = positions[idx]
                        circle = Circle(x, y, 6)
                        circle.fillColor = colors.HexColor('#3B82F6')
                        circle.strokeColor = colors.black
                        circle.strokeWidth = 2
                        d.add(circle)
                
                # Dibujar líneas conectando los puntos
                for i in range(len(patron_numeros) - 1):
                    if 1 <= patron_numeros[i] <= 9 and 1 <= patron_numeros[i+1] <= 9:
                        idx1 = patron_numeros[i] - 1
                        idx2 = patron_numeros[i+1] - 1
                        x1, y1 = positions[idx1]
                        x2, y2 = positions[idx2]
                        line = Line(x1, y1, x2, y2)
                        line.strokeColor = colors.HexColor('#3B82F6')
                        line.strokeWidth = 2
                        d.add(line)
            except:
                pass  # Si hay error parseando, solo mostrar la cuadrícula vacía
        
        return d
    
    def generar_boleta_pdf(self, reparacion, auto_print=False):
        """Generar PDF de la boleta; si auto_print es True, envía a impresión."""
        # Seleccionar carpeta para guardar
        folder = filedialog.askdirectory(title="Seleccionar carpeta para guardar la boleta")
        if not folder:
            return
        
        try:
            # Obtener configuración de la empresa
            config = self.config_model.obtener_configuracion()
            
            # Crear PDF en formato A5
            pdf_path = os.path.join(folder, f"Presupuesto_{reparacion['numero_orden']}.pdf")
            from reportlab.lib.pagesizes import A4
            doc = SimpleDocTemplate(pdf_path, pagesize=A4, topMargin=0.2*inch, bottomMargin=0.2*inch, 
                                   leftMargin=0.3*inch, rightMargin=0.3*inch)
            
            story = []
            styles = getSampleStyleSheet()
            
            # Estilo personalizado para el encabezado
            header_style = ParagraphStyle('header', parent=styles['Normal'], fontSize=16, textColor=colors.black, 
                                         alignment=1, spaceAfter=6)
            small_style = ParagraphStyle('small', parent=styles['Normal'], fontSize=7, alignment=1)
            
            # ENCABEZADO - Tabla con logo, nombre empresa, número y fecha manual
            header_data = []
            logo_cell = ''
            if config.get('logo_path') and os.path.exists(config['logo_path']):
                try:
                    logo_cell = RLImage(config['logo_path'], width=1.3*inch, height=1.3*inch)
                except:
                    logo_cell = ''

            empresa_info = f"""<b style="font-size: 16">{config.get('nombre_sistema', 'EMPRESA')}</b><br/>
<font size="8">☎ {config.get('telefono', 'N/A')}<br/>
{config.get('direccion', 'N/A')}<br/>
CUIT: {config.get('cuit', 'N/A')}</font>"""

            numero_info = f"""<b style="font-size: 18">PRESUPUESTO</b><br/>
<font size="9">N° {reparacion['numero_orden']}</font>"""

            # Celdas para completar manualmente día/mes/año (dentro del cuadro de la derecha)
            fecha_data = [
                ['Día', 'Mes', 'Año'],
                ['', '', '']
            ]
            fecha_table = Table(fecha_data, colWidths=[0.6*inch, 0.6*inch, 0.6*inch])
            fecha_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))

            right_cell = Table(
                [
                    [Paragraph(numero_info, small_style)],
                    [fecha_table]
                ],
                colWidths=[2*inch]
            )
            right_cell.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))

            header_data.append([logo_cell, Paragraph(empresa_info, small_style), right_cell])

            header_table = Table(header_data, colWidths=[1.6*inch, 3.2*inch, 2.4*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ]))
            story.append(header_table)
            
            story.append(Spacer(1, 0.1*inch))
            
            # DATOS DEL CLIENTE
            cliente_data = [
                ['Señor/es:', reparacion['cliente_nombre'], 'D.N.I.:', reparacion.get('numero_serie', ''), 'Tel:', reparacion['cliente_telefono'] or ''],
            ]
            
            cliente_table = Table(cliente_data, colWidths=[0.7*inch, 2.5*inch, 0.6*inch, 1.2*inch, 0.5*inch, 1*inch])
            cliente_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
                ('FONTNAME', (4, 0), (4, 0), 'Helvetica-Bold'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(cliente_table)
            story.append(Spacer(1, 0.05*inch))
            
            # MARCA Y MODELO
            marca_data = [
                ['Marca y Modelo:', reparacion['dispositivo'] + ' - ' + (reparacion['modelo'] or 'N/A')],
            ]
            marca_table = Table(marca_data, colWidths=[1.5*inch, 5*inch])
            marca_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(marca_table)
            story.append(Spacer(1, 0.03*inch))
            
            # ESTADO INICIAL Y SEGURIDAD
            check_si = '[X]' if reparacion.get('sin_bateria') == 1 else '[ ]'
            check_rajado = '[X]' if reparacion.get('rajado') == 1 else '[ ]'
            check_mojado = '[X]' if reparacion.get('mojado') == 1 else '[ ]'
            
            estado_data = [
                ['Estado Inicial:', f'{check_si} Sin Batería    {check_rajado} Rajado    {check_mojado} Mojado'],
            ]
            
            # Si hay contraseña, agregar
            if reparacion.get('contrasena'):
                estado_data.append(['Contraseña:', reparacion.get('contrasena', '')])
            
            estado_table = Table(estado_data, colWidths=[1.5*inch, 5*inch])
            estado_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            story.append(estado_table)
            
            # Si hay patrón, mostrar cuadrícula visual con secuencia
            if reparacion.get('patron'):
                story.append(Spacer(1, 0.03*inch))
                patron_grid = self.crear_patron_grid(reparacion.get('patron', ''))
                
                # Generar secuencia legible
                patron_str = reparacion.get('patron', '')
                try:
                    patron_numeros = [int(n.strip()) for n in patron_str.replace(',', '-').split('-') if n.strip().isdigit()]
                    secuencia_texto = ' → '.join(map(str, patron_numeros))
                except:
                    secuencia_texto = patron_str
                
                # Tabla con patrón y secuencia
                patron_info = f"Secuencia: {secuencia_texto}"
                patron_data = [
                    ['Patrón:', patron_grid, '', patron_info],
                ]
                patron_table = Table(patron_data, colWidths=[1*inch, 1.2*inch, 0.4*inch, 3.9*inch])
                patron_table.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                    ('BOX', (0, 0), (-1, -1), 1, colors.black),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(patron_table)
            
            story.append(Spacer(1, 0.03*inch))
            
            # FALLA DETECTADA
            falla_data = [
                ['Falla detectada:', reparacion['problema'][:200] + ('...' if len(reparacion['problema']) > 200 else '')],
            ]
            falla_table = Table(falla_data, colWidths=[1.5*inch, 5*inch])
            falla_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(falla_table)
            story.append(Spacer(1, 0.05*inch))
            
            # PRECIOS - Seña, Total y Saldo
            saldo = reparacion['total'] - reparacion['sena']
            precios_data = [
                ['Precio $', 'Seña $', 'Saldo $'],
                [f"${int(reparacion['total'])}", f"${int(reparacion['sena'])}", f"${int(saldo)}"],
            ]
            precios_table = Table(precios_data, colWidths=[2.17*inch, 2.17*inch, 2.16*inch])
            precios_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ]))
            story.append(precios_table)
            story.append(Spacer(1, 0.05*inch))
            
            # OBSERVACIONES CON LÍNEAS EN BLANCO
            obs_text = reparacion['observaciones'] if reparacion['observaciones'] else ''
            obs_data = [
                ['OBSERVACIONES:'],
                [obs_text if obs_text else ''],
            ]
            obs_table = Table(obs_data, colWidths=[6.5*inch])
            obs_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 25),  # Espacio moderado para escribir
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(obs_table)
            story.append(Spacer(1, 0.1*inch))
            
            # CONDICIONES (PIE DE PÁGINA)
            condiciones = """<font size=8><b>CONDICIONES:</b></font> <b><font size=7>Estimado cliente, Queremos brindarle la mejor experiencia en nuestro servicio de reparación de celulares. Por favor, tenga en cuenta las siguientes condiciones antes de dejar su equipo:Retiro del equipo: Retiro del equipos dentro de los 30 días posteriores a su reparación tendrá un recargo del 50% sobre el precio pactado. Si transcurren 45 días desde la fecha de recepción, el equipo se considerará abandonado, conforme a los artículos 2525 y 2526 del Código Civil. En tal caso, la empresa podrá disponer del mismo en concepto de compensación de tiempo prestado y el costo de almacenamiento. Responsabilidad sobre la información y procedencia del equipo: No nos hacemos responsables por la pérdida parcial o total de la información contenida en el dispositivo. Asimismo, el cliente asume total responsabilidad por la procedencia del equipo entregado. Garantía sobre equipos mojados, celulares que han sufrido daños por humedad o contacto con líquidos no cuentan con ningún tipo de garantía una vez reparados. Garantía de reparación: La reparación del equipo está garantizada por tres días hábiles a partir de la fecha de entrega, siempre que el dispositivo no presente daños físicos posteriores, como golpes o rupturas, y que conserve el film protector en la pantalla. Agradecemos su confianza en nuestro servicio. Estamos aquí para ayudarle a mantener su dispositivo en óptimas condiciones.</font></b>"""
            cond_table = Table([[Paragraph(condiciones, styles['Normal'])]], colWidths=[6.5*inch])
            cond_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 3, colors.black),
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(cond_table)
            
            # PIE DE PÁGINA CON FIRMA
            story.append(Spacer(1, 0.08*inch))
            
            firma_data = [
                ['', '', ''],
                ['_________________________', '', '_________________________'],
                ['Firma del Técnico', '', 'RECIBI CONFORME'],
            ]
            firma_table = Table(firma_data, colWidths=[2*inch, 2.5*inch, 2*inch])
            firma_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(firma_table)
            
            # Generar PDF
            doc.build(story)

            # Imprimir automáticamente si se solicita (solo Windows)
            if auto_print:
                try:
                    os.startfile(pdf_path, "print")
                except Exception as e:
                    messagebox.showwarning("Impresión", f"No se pudo enviar a la impresora automáticamente:\n{str(e)}")
            
            messagebox.showinfo("Éxito", f"Presupuesto guardado en:\n{pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el presupuesto:\n{str(e)}")
    
    
    def ver_galeria_fotos(self):
        """Mostrar galería de fotos en una ventana (temporales si es nueva, actuales si es edición)"""
        if self.modo_edicion:
            fotos = self.fotos_actuales
        else:
            fotos = getattr(self, 'fotos_temporales', [])
        if not fotos:
            messagebox.showinfo("Información", "No hay fotos para mostrar")
            return
        from PIL import Image, ImageTk
        parent_window = None
        if hasattr(self, 'form_window') and self.form_window and self.form_window.winfo_exists():
            parent_window = self.form_window
        else:
            parent_window = self.parent

        try:
            if parent_window.grab_current() == parent_window:
                parent_window.grab_release()
        except tk.TclError:
            pass

        galeria_window = tk.Toplevel(parent_window)
        galeria_window.title("Galería de Fotos")
        galeria_window.geometry("600x500")
        try:
            galeria_window.transient(parent_window)
        except tk.TclError:
            pass
        galeria_window.grab_set()
        fotos_frame = ttk.Frame(galeria_window)
        fotos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        canvas = tk.Canvas(fotos_frame, bg='white')
        scrollbar = ttk.Scrollbar(fotos_frame, orient=tk.VERTICAL, command=canvas.yview)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.config(yscrollcommand=scrollbar.set)
        interior = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=interior, anchor=tk.NW)
        for i, foto_path in enumerate(fotos, 1):
            try:
                # Validar que el archivo existe
                if not os.path.exists(foto_path):
                    tk.Label(interior, text=f"⚠️ Foto {i} no encontrada: {foto_path}", bg='white', fg='orange').pack()
                    continue
                    
                img = Image.open(foto_path)
                img.thumbnail((500, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                frame_foto = tk.Frame(interior, bg='white', relief=tk.SUNKEN, bd=1)
                frame_foto.pack(fill=tk.BOTH, padx=5, pady=5)
                lbl_img = tk.Label(frame_foto, image=photo, bg='white')
                lbl_img.image = photo
                lbl_img.pack()
                # Botón para eliminar solo si es temporal
                if not self.modo_edicion:
                    btn_eliminar = tk.Button(frame_foto, text="❌ Eliminar", command=lambda idx=i-1: self.eliminar_foto_temporal(idx, galeria_window))
                    btn_eliminar.pack(pady=5)
            except Exception as e:
                tk.Label(interior, text=f"Error al cargar foto {i}: {str(e)}", bg='white', fg='red').pack()
        def on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox('all'))
        interior.bind('<Configure>', on_frame_configure)

        def _cerrar_galeria():
            try:
                galeria_window.grab_release()
            except tk.TclError:
                pass
            if hasattr(self, 'form_window') and self.form_window and self.form_window.winfo_exists():
                try:
                    self.form_window.grab_set()
                except tk.TclError:
                    pass
            galeria_window.destroy()

        galeria_window.protocol("WM_DELETE_WINDOW", _cerrar_galeria)

    def eliminar_foto_temporal(self, idx, galeria_window=None):
        """Eliminar una foto temporal antes de guardar la reparación"""
        if hasattr(self, 'fotos_temporales') and 0 <= idx < len(self.fotos_temporales):
            import os
            try:
                os.remove(self.fotos_temporales[idx])
            except Exception:
                pass
            del self.fotos_temporales[idx]
            self.actualizar_contador_fotos_temporales()
            if galeria_window:
                galeria_window.destroy()
                self.ver_galeria_fotos()
    
    def eliminar_foto_id(self, numero_foto):
        """Eliminar una foto específica"""
        if not self.reparacion_actual:
            return
        
        reparacion_id = self.reparacion_actual['id']
        exito, resultado = self.reparacion_model.eliminar_foto(reparacion_id, numero_foto)
        
        if exito:
            self.fotos_actuales = self.reparacion_model.obtener_fotos(reparacion_id)
            self.actualizar_contador_fotos()
            messagebox.showinfo("Éxito", "Foto eliminada correctamente")
        else:
            messagebox.showerror("Error", f"No se pudo eliminar la foto:\n{resultado}")
    
    def eliminar_todas_fotos(self):
        """Eliminar todas las fotos de la reparación"""
        if not self.reparacion_actual:
            messagebox.showwarning("Advertencia", "Primero debes seleccionar una reparación")
            return
        
        if not self.fotos_actuales:
            messagebox.showinfo("Información", "No hay fotos para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar todas las {len(self.fotos_actuales)} fotos?"):
            reparacion_id = self.reparacion_actual['id']
            exito, resultado = self.reparacion_model.eliminar_todas_fotos(reparacion_id)
            
            if exito:
                self.fotos_actuales = []
                self.actualizar_contador_fotos()
                messagebox.showinfo("Éxito", "Todas las fotos han sido eliminadas")
            else:
                messagebox.showerror("Error", f"Error al eliminar fotos:\n{resultado}")
    
    def actualizar_contador_fotos(self):
        """Actualizar el contador de fotos (edición)"""
        if hasattr(self, 'fotos_label'):
            if self.modo_edicion:
                cantidad = len(self.fotos_actuales)
            else:
                cantidad = len(getattr(self, 'fotos_temporales', []))
            self.fotos_label.config(text=f"Fotos: {cantidad}")
    
    def cargar_fotos_reparacion(self, reparacion_id):
        """Cargar fotos de una reparación"""
        fotos = self.reparacion_model.obtener_fotos(reparacion_id)
        # Validar que los archivos existan
        self.fotos_actuales = [foto for foto in fotos if os.path.exists(foto)]
        self.fotos_temporales = []  # Limpiar fotos temporales al cargar una reparación
        self.actualizar_contador_fotos()

    def buscar_cliente(self):
        """Filtrar reparaciones por nombre de cliente"""
        termino_busqueda = self.buscar_cliente_var.get().lower().strip()
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not termino_busqueda:
            # Si el campo está vacío, mostrar todas
            self.cargar_reparaciones()
            return
        
        # Obtener todas las reparaciones
        reparaciones = self.reparacion_model.obtener_reparaciones()
        
        # Filtrar por cliente
        for rep in reparaciones:
            cliente = rep['cliente_nombre'].lower()
            if termino_busqueda in cliente:
                # Convertir estado
                estado_ui = self.estado_db_to_ui(rep['estado'])
                
                # Formatear fechas
                fecha = rep['fecha_creacion'][:10] if rep['fecha_creacion'] else 'N/A'
                
                self.tree.insert('', tk.END, values=(
                    rep['numero_orden'],
                    rep['cliente_nombre'],
                    rep['dispositivo'],
                    estado_ui,
                    f"${rep['sena']:.2f}" if rep['sena'] else '$0.00',
                    f"${rep['total']:.2f}",
                    fecha,
                    'Ver'
                ))
    
    def limpiar_busqueda(self):
        """Limpiar el campo de búsqueda y mostrar todas las reparaciones"""
        self.buscar_cliente_var.set('')
        self.cargar_reparaciones()

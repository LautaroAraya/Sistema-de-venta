import tkinter as tk
from tkinter import ttk, messagebox
from models.producto import Producto
from models.venta import Venta
from datetime import datetime
import os
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import tempfile
from PIL import Image as PILImage

class CelularesView:
    def __init__(self, parent, db_manager, user_data):
        self.parent = parent
        self.db_manager = db_manager
        self.user_data = user_data
        self.producto_model = Producto(db_manager)
        self.venta_model = Venta(db_manager)
        
        # Variables para el formulario
        self.cliente_nombre_var = tk.StringVar()
        self.cliente_documento_var = tk.StringVar()
        self.cliente_telefono_var = tk.StringVar()
        self.cliente_email_var = tk.StringVar()
        self.telefono_marca_var = tk.StringVar()
        self.telefono_modelo_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.sena_var = tk.StringVar(value="0.00")
        self.total_var = tk.StringVar(value="0.00")
        
        self.ventas_realizadas = []
        self.create_widgets()
        self.cargar_ventas()

    def create_widgets(self):
        """Crear widgets de la vista de venta de celulares"""
        self.parent.configure(bg='#F0F4F8')

        # Título
        title_frame = tk.Frame(self.parent, bg='#8B5CF6', height=60)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        title_frame.pack_propagate(False)

        tk.Label(title_frame,
                 text="📱 VENTA DE CELULARES",
                 font=("Arial", 18, "bold"),
                 bg='#8B5CF6',
                 fg='white').pack(expand=True)

        # Contenedor principal
        parent = tk.Frame(self.parent, bg='#F0F4F8')
        parent.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        # Lista de ventas
        list_frame = tk.Frame(parent, bg='white', bd=1, relief=tk.RIDGE, padx=10, pady=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        columns = ('numero', 'cliente', 'telefono', 'sena', 'total', 'fecha')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        headings = ['N° Venta', 'Cliente', 'Teléfono', 'Seña', 'Total', 'Fecha']
        for col, head in zip(columns, headings):
            self.tree.heading(col, text=head)
        
        self.tree.column('numero', width=120)
        self.tree.column('cliente', width=150)
        self.tree.column('telefono', width=120)
        self.tree.column('sena', width=100)
        self.tree.column('total', width=100)
        self.tree.column('fecha', width=100)

        yscroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Botonera de acciones
        actions_frame = tk.Frame(self.parent, bg='#F0F4F8')
        actions_frame.pack(pady=(0, 10))
        
        btn_nueva = tk.Button(actions_frame, text="➕ Nueva Venta", font=('Arial', 11, 'bold'), 
                             bg='#10B981', fg='white', activebackground='#059669', bd=0, 
                             pady=10, cursor='hand2', command=self.abrir_formulario_venta)
        btn_nueva.pack(side=tk.LEFT, padx=5, ipadx=10)
        
        btn_editar = tk.Button(actions_frame, text="✏️ Editar", font=('Arial', 11, 'bold'), 
                              bg='#F59E0B', fg='white', activebackground='#D97706', bd=0, 
                              pady=10, cursor='hand2', command=self.editar_venta)
        btn_editar.pack(side=tk.LEFT, padx=5, ipadx=10)
        
        btn_eliminar = tk.Button(actions_frame, text="🗑️ Eliminar", font=('Arial', 11, 'bold'), 
                                bg='#EF4444', fg='white', activebackground='#B91C1C', bd=0, 
                                pady=10, cursor='hand2', command=self.eliminar_venta)
        btn_eliminar.pack(side=tk.LEFT, padx=5, ipadx=10)
        
        btn_imprimir = tk.Button(actions_frame, text="🖨️ Imprimir", font=('Arial', 11, 'bold'), 
                                bg='#3B82F6', fg='white', activebackground='#1D4ED8', bd=0, 
                                pady=10, cursor='hand2', command=self.imprimir_comprobante)
        btn_imprimir.pack(side=tk.LEFT, padx=5, ipadx=10)

    def cargar_ventas(self):
        """Cargar lista de ventas desde la base de datos"""
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT numero_venta, cliente_nombre, cliente_telefono, sena, total, fecha_venta
                FROM ventas_celulares
                ORDER BY fecha_venta DESC
                LIMIT 100
            ''')
            
            ventas = cursor.fetchall()
            for venta in ventas:
                fecha = venta[5].split(' ')[0] if venta[5] else 'N/A'
                self.tree.insert('', 'end', values=(
                    venta[0],  # numero_venta
                    venta[1],  # cliente_nombre
                    venta[2] or '',  # cliente_telefono
                    f"${venta[3]:.2f}",  # sena
                    f"${venta[4]:.2f}",  # total
                    fecha
                ))
        except Exception as e:
            print(f"Error al cargar ventas: {str(e)}")

    def abrir_formulario_venta(self):
        """Abrir formulario para crear nueva venta"""
        top = tk.Toplevel(self.parent)
        top.title("Nueva Venta de Celulares")
        top.grab_set()
        top.geometry("1000x600")
        top.configure(bg='#F0F4F8')

        # Canvas con scrollbar
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

        # Datos del cliente
        tk.Label(form_frame, text="Datos del Cliente", font=("Arial", 12, "bold"), bg='white', fg='#8B5CF6').grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=10, padx=5)
        
        tk.Label(form_frame, text="Nombre:", font=("Arial", 10, "bold"), bg='white').grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.cliente_nombre_var, font=("Arial", 10), width=30).grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Documento:", font=("Arial", 10, "bold"), bg='white').grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.cliente_documento_var, font=("Arial", 10), width=20).grid(row=1, column=3, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Teléfono:", font=("Arial", 10, "bold"), bg='white').grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.cliente_telefono_var, font=("Arial", 10), width=30).grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Email:", font=("Arial", 10, "bold"), bg='white').grid(row=2, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.cliente_email_var, font=("Arial", 10), width=20).grid(row=2, column=3, sticky=tk.EW, pady=5, padx=5)

        # Separador
        tk.Frame(form_frame, height=2, bg='#E5E7EB').grid(row=3, column=0, columnspan=4, sticky=tk.EW, pady=15, padx=5)

        # Datos del celular
        tk.Label(form_frame, text="Datos del Celular", font=("Arial", 12, "bold"), bg='white', fg='#8B5CF6').grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=10, padx=5)

        tk.Label(form_frame, text="Marca:", font=("Arial", 10, "bold"), bg='white').grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.telefono_marca_var, font=("Arial", 10), width=30).grid(row=5, column=1, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Modelo:", font=("Arial", 10, "bold"), bg='white').grid(row=5, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.telefono_modelo_var, font=("Arial", 10), width=20).grid(row=5, column=3, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Descripción:", font=("Arial", 10, "bold"), bg='white').grid(row=6, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.descripcion_var, font=("Arial", 10), width=30).grid(row=6, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=5)

        # Separador
        tk.Frame(form_frame, height=2, bg='#E5E7EB').grid(row=7, column=0, columnspan=4, sticky=tk.EW, pady=15, padx=5)

        # Detalles de la venta
        tk.Label(form_frame, text="Detalles de la Venta", font=("Arial", 12, "bold"), bg='white', fg='#8B5CF6').grid(row=8, column=0, columnspan=4, sticky=tk.W, pady=10, padx=5)

        tk.Label(form_frame, text="Total ($):", font=("Arial", 10, "bold"), bg='white').grid(row=9, column=0, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.total_var, font=("Arial", 10), width=30).grid(row=9, column=1, sticky=tk.EW, pady=5, padx=5)

        tk.Label(form_frame, text="Seña ($):", font=("Arial", 10, "bold"), bg='white').grid(row=9, column=2, sticky=tk.W, pady=5, padx=5)
        ttk.Entry(form_frame, textvariable=self.sena_var, font=("Arial", 10), width=20).grid(row=9, column=3, sticky=tk.EW, pady=5, padx=5)

        # Botones
        btn_frame = tk.Frame(form_frame, bg='white')
        btn_frame.grid(row=10, column=0, columnspan=4, sticky=tk.EW, pady=20, padx=5)

        tk.Button(btn_frame, text="💾 Guardar Venta", font=("Arial", 10, "bold"), bg='#10B981', fg='white',
                 command=lambda: self.guardar_venta_modal(top)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="❌ Cancelar", font=("Arial", 10, "bold"), bg='#EF4444', fg='white',
                 command=top.destroy).pack(side=tk.LEFT, padx=5)

    def cargar_celulares_tabla(self):
        """Cargar celulares en la tabla de disponibles"""
        for item in self.celulares_tree.get_children():
            self.celulares_tree.delete(item)

        productos = self.producto_model.listar_productos(activos_solo=True)
        for producto in productos:
            self.celulares_tree.insert('', 'end', values=(
                producto['codigo'],
                producto['nombre'][:30],
                f"${producto['precio']:.2f}",
                producto['stock'],
                1,
                "Agregar"
            ))

    def guardar_venta_modal(self, top):
        """Guardar la venta desde el modal"""
        try:
            cliente = self.cliente_nombre_var.get() or "Cliente General"
            documento = self.cliente_documento_var.get() or ""
            telefono = self.cliente_telefono_var.get() or ""
            email = self.cliente_email_var.get() or ""
            marca = self.telefono_marca_var.get() or ""
            modelo = self.telefono_modelo_var.get() or ""
            descripcion = self.descripcion_var.get() or ""
            
            try:
                total = float(self.total_var.get() or 0)
            except:
                total = 0
            
            try:
                sena = float(self.sena_var.get() or 0)
            except:
                sena = 0

            # Crear número de venta
            numero_venta = f"CEL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Guardar en base de datos
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            try:
                fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute('''
                                        INSERT INTO ventas_celulares 
                                        (numero_venta, usuario_id, cliente_nombre, cliente_documento, cliente_telefono, 
                                         cliente_email, telefono_marca, telefono_modelo, descripcion, subtotal, descuento, total, sena, fecha_venta)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (numero_venta, self.user_data['id'], cliente, documento, telefono, 
                                            email, marca, modelo, descripcion, 0, 0, total, sena, fecha_actual))
                
                conn.commit()
                
                messagebox.showinfo("Venta Registrada", 
                                  f"Venta registrada exitosamente.\n\n"
                                  f"N° Venta: {numero_venta}\n"
                                  f"Cliente: {cliente}\n"
                                  f"Documento: {documento}\n"
                                  f"Teléfono: {telefono}\n"
                                  f"Marca: {marca}\n"
                                  f"Modelo: {modelo}\n"
                                  f"Descripción: {descripcion}\n"
                                  f"Total: ${total:.2f}\n"
                                  f"Seña: ${sena:.2f}")
                
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error al guardar", f"Error: {str(e)}")
                return
            
            # Limpiar formulario
            self.cliente_nombre_var.set("")
            self.cliente_documento_var.set("")
            self.cliente_telefono_var.set("")
            self.cliente_email_var.set("")
            self.telefono_marca_var.set("")
            self.telefono_modelo_var.set("")
            self.descripcion_var.set("")
            self.sena_var.set("0.00")
            self.total_var.set("0.00")
            
            # Recargar tabla
            self.cargar_ventas()
            top.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def editar_venta(self):
        """Editar venta seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Por favor selecciona una venta para editar")
            return
        
        # Obtener datos de la venta seleccionada
        item = seleccion[0]
        valores = self.tree.item(item, 'values')
        numero_venta = valores[0]
        
        # Consultar base de datos para obtener datos completos
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, numero_venta, cliente_nombre, cliente_documento, cliente_telefono, cliente_email,
                       telefono_marca, telefono_modelo, descripcion, total, sena
                FROM ventas_celulares
                WHERE numero_venta = ?
            ''', (numero_venta,))
            
            venta = cursor.fetchone()
            if not venta:
                messagebox.showerror("Error", "No se encontró la venta")
                return
            
            venta_id = venta[0]
            
            # Abrir formulario de edición
            top = tk.Toplevel(self.parent)
            top.title(f"Editar Venta - {numero_venta}")
            top.grab_set()
            top.geometry("1000x600")
            top.configure(bg='#F0F4F8')

            # Canvas con scrollbar
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

            # Variables para el formulario
            edit_cliente_nombre = tk.StringVar(value=venta[2])
            edit_cliente_documento = tk.StringVar(value=venta[3] or "")
            edit_cliente_telefono = tk.StringVar(value=venta[4] or "")
            edit_cliente_email = tk.StringVar(value=venta[5] or "")
            edit_telefono_marca = tk.StringVar(value=venta[6] or "")
            edit_telefono_modelo = tk.StringVar(value=venta[7] or "")
            edit_descripcion = tk.StringVar(value=venta[8] or "")
            edit_total = tk.StringVar(value=f"{venta[9]:.2f}")
            edit_sena = tk.StringVar(value=f"{venta[10]:.2f}")

            # Datos del cliente
            tk.Label(form_frame, text="Datos del Cliente", font=("Arial", 12, "bold"), bg='white', fg='#8B5CF6').grid(row=0, column=0, columnspan=4, sticky=tk.W, pady=10, padx=5)
            
            tk.Label(form_frame, text="Nombre:", font=("Arial", 10, "bold"), bg='white').grid(row=1, column=0, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_cliente_nombre, font=("Arial", 10), width=30).grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)

            tk.Label(form_frame, text="Documento:", font=("Arial", 10, "bold"), bg='white').grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_cliente_documento, font=("Arial", 10), width=20).grid(row=1, column=3, sticky=tk.EW, pady=5, padx=5)

            tk.Label(form_frame, text="Teléfono:", font=("Arial", 10, "bold"), bg='white').grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_cliente_telefono, font=("Arial", 10), width=30).grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)

            tk.Label(form_frame, text="Email:", font=("Arial", 10, "bold"), bg='white').grid(row=2, column=2, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_cliente_email, font=("Arial", 10), width=20).grid(row=2, column=3, sticky=tk.EW, pady=5, padx=5)

            # Separador
            tk.Frame(form_frame, height=2, bg='#E5E7EB').grid(row=3, column=0, columnspan=4, sticky=tk.EW, pady=15, padx=5)

            # Datos del celular
            tk.Label(form_frame, text="Datos del Celular", font=("Arial", 12, "bold"), bg='white', fg='#8B5CF6').grid(row=4, column=0, columnspan=4, sticky=tk.W, pady=10, padx=5)

            tk.Label(form_frame, text="Marca:", font=("Arial", 10, "bold"), bg='white').grid(row=5, column=0, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_telefono_marca, font=("Arial", 10), width=30).grid(row=5, column=1, sticky=tk.EW, pady=5, padx=5)

            tk.Label(form_frame, text="Modelo:", font=("Arial", 10, "bold"), bg='white').grid(row=5, column=2, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_telefono_modelo, font=("Arial", 10), width=20).grid(row=5, column=3, sticky=tk.EW, pady=5, padx=5)

            tk.Label(form_frame, text="Descripción:", font=("Arial", 10, "bold"), bg='white').grid(row=6, column=0, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_descripcion, font=("Arial", 10), width=30).grid(row=6, column=1, columnspan=3, sticky=tk.EW, pady=5, padx=5)

            # Separador
            tk.Frame(form_frame, height=2, bg='#E5E7EB').grid(row=7, column=0, columnspan=4, sticky=tk.EW, pady=15, padx=5)

            # Detalles de la venta
            tk.Label(form_frame, text="Detalles de la Venta", font=("Arial", 12, "bold"), bg='white', fg='#8B5CF6').grid(row=8, column=0, columnspan=4, sticky=tk.W, pady=10, padx=5)

            tk.Label(form_frame, text="Total ($):", font=("Arial", 10, "bold"), bg='white').grid(row=9, column=0, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_total, font=("Arial", 10), width=30).grid(row=9, column=1, sticky=tk.EW, pady=5, padx=5)

            tk.Label(form_frame, text="Seña ($):", font=("Arial", 10, "bold"), bg='white').grid(row=9, column=2, sticky=tk.W, pady=5, padx=5)
            ttk.Entry(form_frame, textvariable=edit_sena, font=("Arial", 10), width=20).grid(row=9, column=3, sticky=tk.EW, pady=5, padx=5)

            # Botones
            btn_frame = tk.Frame(form_frame, bg='white')
            btn_frame.grid(row=10, column=0, columnspan=4, sticky=tk.EW, pady=20, padx=5)

            def guardar_cambios():
                try:
                    cliente = edit_cliente_nombre.get() or "Cliente General"
                    documento = edit_cliente_documento.get() or ""
                    telefono = edit_cliente_telefono.get() or ""
                    email = edit_cliente_email.get() or ""
                    marca = edit_telefono_marca.get() or ""
                    modelo = edit_telefono_modelo.get() or ""
                    descripcion = edit_descripcion.get() or ""
                    
                    try:
                        total = float(edit_total.get() or 0)
                    except:
                        total = 0
                    
                    try:
                        sena = float(edit_sena.get() or 0)
                    except:
                        sena = 0

                    # Actualizar en base de datos
                    conn = self.db_manager.get_connection()
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute('''
                            UPDATE ventas_celulares
                            SET cliente_nombre = ?, cliente_documento = ?, cliente_telefono = ?,
                                cliente_email = ?, telefono_marca = ?, telefono_modelo = ?,
                                descripcion = ?, total = ?, sena = ?
                            WHERE id = ?
                        ''', (cliente, documento, telefono, email, marca, modelo, descripcion, total, sena, venta_id))
                        
                        conn.commit()
                        messagebox.showinfo("Éxito", f"Venta actualizada correctamente")
                        self.cargar_ventas()
                        top.destroy()
                        
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Error al actualizar", f"Error: {str(e)}")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar: {str(e)}")

            tk.Button(btn_frame, text="💾 Guardar Cambios", font=("Arial", 10, "bold"), bg='#10B981', fg='white',
                     command=guardar_cambios).pack(side=tk.LEFT, padx=5)
            
            tk.Button(btn_frame, text="❌ Cancelar", font=("Arial", 10, "bold"), bg='#EF4444', fg='white',
                     command=top.destroy).pack(side=tk.LEFT, padx=5)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar: {str(e)}")

    def eliminar_venta(self):
        """Eliminar venta seleccionada"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Por favor selecciona una venta para eliminar")
            return
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar esta venta?"):
            # Obtener datos de la venta seleccionada
            item = seleccion[0]
            valores = self.tree.item(item, 'values')
            numero_venta = valores[0]
            
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM ventas_celulares WHERE numero_venta = ?', (numero_venta,))
                conn.commit()
                messagebox.showinfo("Éxito", "Venta eliminada correctamente")
                self.cargar_ventas()
                
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")
    
    def imprimir_comprobante(self):
        """Imprimir comprobante de venta seleccionada como PDF"""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Seleccionar", "Por favor selecciona una venta para imprimir")
            return
        
        # Obtener datos de la venta seleccionada
        item = seleccion[0]
        valores = self.tree.item(item, 'values')
        numero_venta = valores[0]
        
        # Consultar base de datos para obtener datos completos
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                  SELECT numero_venta, cliente_nombre, cliente_documento, cliente_telefono, cliente_email,
                      telefono_marca, telefono_modelo, descripcion, total, sena, fecha_venta
                FROM ventas_celulares
                WHERE numero_venta = ?
            ''', (numero_venta,))
            
            venta = cursor.fetchone()
            if not venta:
                messagebox.showerror("Error", "No se encontró la venta")
                return
            
            # Obtener configuración del sistema
            cursor.execute('SELECT nombre_sistema, logo_path, telefono, direccion, cuit FROM configuracion WHERE id = 1')
            config = cursor.fetchone()
            
            # Generar PDF del comprobante
            pdf_path = self._generar_pdf_comprobante(venta, config)
            
            # Abrir PDF
            os.startfile(pdf_path)
            messagebox.showinfo("Éxito", f"Comprobante guardado y abierto.\nRuta: {pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al imprimir: {str(e)}")
    
    def _generar_pdf_comprobante(self, venta, config):
        """Generar PDF del comprobante"""
        numero_venta = venta[0]
        cliente_nombre = venta[1]
        cliente_documento = venta[2]
        cliente_telefono = venta[3]
        cliente_email = venta[4]
        marca = venta[5]
        modelo = venta[6]
        descripcion = venta[7]
        total = float(venta[8])
        sena = float(venta[9])
        fecha = venta[10]
        saldo = total - sena
        
        # Datos de configuración
        nombre_sistema = config[0] if config and config[0] else "SISTEMA DE VENTAS"
        logo_path = config[1] if config and config[1] else None
        telefono_empresa = config[2] if config and config[2] else ""
        direccion_empresa = config[3] if config and config[3] else ""
        cuit_empresa = config[4] if config and config[4] else ""
        
        # Crear archivo temporal para el PDF
        temp_dir = tempfile.gettempdir()
        pdf_filename = f"Comprobante_{numero_venta}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        # Crear documento PDF con márgenes más generosos
        doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                               rightMargin=0.75*inch, leftMargin=0.75*inch,
                               topMargin=0.6*inch, bottomMargin=0.6*inch)
        
        # Contenedor de elementos
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Estilo para título principal
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=13,
            textColor=colors.HexColor('#8B5CF6'),
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Estilo para subtítulo
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            spaceAfter=1,
            alignment=TA_CENTER
        )
        
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=9,
            textColor=colors.white,
            backColor=colors.HexColor('#8B5CF6'),
            spaceAfter=8,
            spaceBefore=2,
            leftIndent=8,
            rightIndent=8,
            fontName='Helvetica-Bold'
        )
        
        # ========== ENCABEZADO ==========
        header_data = []

        # Logo centrado
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image(logo_path, width=0.75*inch, height=0.75*inch)
                header_data.append([img])
            except:
                pass

        # Nombre de empresa centrado
        header_data.append([Paragraph(f"<b>{nombre_sistema}</b>", title_style)])
        
        # Datos de empresa en segunda fila
        empresa_info_parts = []
        if cuit_empresa:
            empresa_info_parts.append(f"CUIT: {cuit_empresa}")
        if telefono_empresa:
            empresa_info_parts.append(f"Tel: {telefono_empresa}")
        
        empresa_info = " | ".join(empresa_info_parts)
        if empresa_info:
            header_data.append([Paragraph(empresa_info, subtitle_style)])
        
        if direccion_empresa:
            header_data.append([Paragraph(f"<i>{direccion_empresa}</i>", subtitle_style)])
        
        # Tabla del encabezado sin bordes visibles
        header_table = Table(header_data, colWidths=[6.75*inch], hAlign='CENTER')
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Línea divisoria
        elements.append(Paragraph("<hr/>", styles['Normal']))
        elements.append(Spacer(1, 0.08*inch))
        
        # ========== NÚMERO DE COMPROBANTE ==========
        elements.append(Paragraph(f"<b>COMPROBANTE DE VENTA</b>", ParagraphStyle(
            'ComprobanteTitulo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=4
        )))
        
        elements.append(Paragraph(f"<b style='color: #8B5CF6; font-size: 12pt'>{numero_venta}</b>", ParagraphStyle(
            'NumeroComprobante',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=12
        )))
        
        # ========== SECCIÓN: DATOS DEL CLIENTE ==========
        section_width = 5.75 * inch
        cliente_header = Table([[Paragraph("DATOS DEL CLIENTE", section_style)]], colWidths=[section_width], hAlign='CENTER')
        cliente_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#8B5CF6')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(cliente_header)
        
        cliente_data = [
            ["Nombre:", cliente_nombre],
            ["Documento:", cliente_documento if cliente_documento else "-"],
            ["Teléfono:", cliente_telefono if cliente_telefono else "-"],
            ["Email:", cliente_email if cliente_email else "-"],
        ]
        
        cliente_table = Table(cliente_data, colWidths=[1.6*inch, 4.15*inch], hAlign='CENTER')
        cliente_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ]))
        
        elements.append(cliente_table)
        elements.append(Spacer(1, 0.12*inch))
        
        # ========== SECCIÓN: DATOS DEL CELULAR ==========
        celular_header = Table([[Paragraph("DATOS DEL CELULAR", section_style)]], colWidths=[section_width], hAlign='CENTER')
        celular_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#8B5CF6')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(celular_header)
        
        celular_data = [
            ["Marca:", marca if marca else "-"],
            ["Modelo:", modelo if modelo else "-"],
            ["Descripción:", descripcion if descripcion else "-"],
        ]
        
        celular_table = Table(celular_data, colWidths=[1.6*inch, 4.15*inch], hAlign='CENTER')
        celular_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ]))
        
        elements.append(celular_table)
        elements.append(Spacer(1, 0.12*inch))
        
        # ========== SECCIÓN: RESUMEN FINANCIERO ==========
        resumen_header = Table([[Paragraph("RESUMEN FINANCIERO", section_style)]], colWidths=[section_width], hAlign='CENTER')
        resumen_header.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#8B5CF6')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(resumen_header)
        
        # Crear tabla con mejor formato
        totales_data = [
            ["Precio Total:", f"${total:,.2f}"],
            ["Seña Pagada:", f"${sena:,.2f}"],
            ["SALDO A PAGAR:", f"${saldo:,.2f}"],
            ["Fecha:", fecha[:10]],
        ]
        
        totales_table = Table(totales_data, colWidths=[2.2*inch, 3.55*inch], hAlign='CENTER')
        totales_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 2), (1, 2), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 2), (1, 2), colors.HexColor('#FFE8E8')),
            ('TEXTCOLOR', (0, 2), (1, 2), colors.HexColor('#D32F2F')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#333333')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('LINEABOVE', (0, 2), (1, 2), 2, colors.HexColor('#8B5CF6')),
            ('LINEBELOW', (0, 2), (1, 2), 2, colors.HexColor('#8B5CF6')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ]))
        
        elements.append(totales_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # ========== PIE DE PÁGINA ==========
        elements.append(Paragraph("<hr/>", styles['Normal']))
        elements.append(Spacer(1, 0.08*inch))
        
        elements.append(Paragraph("Gracias por su compra", ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=2,
            fontName='Helvetica-Bold'
        )))
        elements.append(Paragraph("Este comprobante fue generado automáticamente", ParagraphStyle(
            'FooterSmall',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#999999'),
            alignment=TA_CENTER
        )))
        
        # Construir PDF
        doc.build(elements)
        
        return pdf_path

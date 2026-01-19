"""
Módulo de Validación de Licencias con Firebase Firestore (SDK Público)
Sistema de licenciamiento remoto SIN credenciales sensibles
"""

import os
import sys
import platform
import subprocess
import uuid
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

try:
    import requests
except ImportError:
    print("Error: requests no está instalado. Ejecuta: pip install requests")
    sys.exit(1)

# Importar configuración de Firebase
try:
    # Agregar la carpeta raíz al path si no está
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)
    
    from firebase_config import FIREBASE_CONFIG, LICENSES_COLLECTION
except ImportError:
    print("Error: No se encontró firebase_config.py")
    print("Crea el archivo firebase_config.py con la configuración de tu proyecto")
    sys.exit(1)


class ValidadorLicencias:
    """Clase para validar licencias mediante Firebase Firestore (SDK público)"""
    
    def __init__(self):
        """Inicializa el validador de licencias"""
        self.db = None
        self.hwid = self.obtener_hwid()
        self._inicializar_firestore()
    
    def obtener_hwid(self):
        """
        Obtiene un identificador único del hardware de la computadora
        
        Returns:
            str: HWID único de la computadora
        """
        try:
            sistema = platform.system()
            
            if sistema == "Windows":
                try:
                    hwid = str(subprocess.check_output('wmic csproduct get uuid', 
                                                       shell=True).decode().split('\n')[1].strip())
                except:
                    try:
                        hwid = str(subprocess.check_output('wmic baseboard get serialnumber', 
                                                           shell=True).decode().split('\n')[1].strip())
                    except:
                        hwid = str(uuid.getnode())
            
            elif sistema == "Linux":
                try:
                    with open('/etc/machine-id', 'r') as f:
                        hwid = f.read().strip()
                except:
                    hwid = str(uuid.getnode())
            
            elif sistema == "Darwin":
                hwid = str(subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | grep UUID", 
                                                   shell=True).decode().split('"')[3])
            else:
                hwid = str(uuid.getnode())
            
            hwid = hwid.replace('-', '').replace(' ', '').upper()
            
            if not hwid or hwid == '' or len(hwid) < 10:
                hwid = uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.getnode())).hex.upper()
            
            return hwid
            
        except Exception as e:
            print(f"Error obteniendo HWID: {e}")
            fallback = uuid.uuid5(uuid.NAMESPACE_DNS, 
                                 f"{platform.node()}-{platform.machine()}-{uuid.getnode()}").hex.upper()
            return fallback
    
    def _inicializar_firestore(self):
        """Inicializa la conexión con Firestore usando REST API"""
        try:
            # Validar configuración
            self.project_id = FIREBASE_CONFIG.get('projectId')
            self.api_key = FIREBASE_CONFIG.get('apiKey')
            
            if not self.project_id or not self.api_key:
                raise ValueError("Faltan projectId o apiKey en firebase_config.py")
            
            # Base URL para Firestore REST API
            self.firestore_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"
            
        except Exception as e:
            self._mostrar_error_configuracion(str(e))
            sys.exit(1)
    
    def validar_licencia(self):
        """
        Valida la licencia de la computadora actual contra Firebase usando REST API
        
        Returns:
            dict: Diccionario con estado de validación y datos
        """
        try:
            # URL del documento específico
            url = f"{self.firestore_url}/{LICENSES_COLLECTION}/{self.hwid}?key={self.api_key}"
            
            # Realizar petición GET
            response = requests.get(url, timeout=10)
            
            # Verificar si el documento existe
            if response.status_code == 404:
                mensaje = f"PC no registrada - ID: {self.hwid}"
                return {
                    'valido': False,
                    'mensaje': mensaje,
                    'dias_restantes': 0,
                    'hwid': self.hwid,
                    'razon': 'no_registrada'
                }
            
            if response.status_code != 200:
                return {
                    'valido': False,
                    'mensaje': f'Error al validar licencia: {response.status_code}',
                    'dias_restantes': 0,
                    'hwid': self.hwid,
                    'razon': 'error_conexion'
                }
            
            # Parsear respuesta
            doc_data = response.json()
            fields = doc_data.get('fields', {})
            
            # Extraer valores de los campos de Firestore
            def get_field_value(field_data):
                """Extrae el valor de un campo de Firestore REST API"""
                if 'booleanValue' in field_data:
                    return field_data['booleanValue']
                elif 'stringValue' in field_data:
                    return field_data['stringValue']
                elif 'timestampValue' in field_data:
                    return field_data['timestampValue']
                elif 'integerValue' in field_data:
                    return int(field_data['integerValue'])
                return None
            
            # Verificar si está activa
            esta_activo = get_field_value(fields.get('esta_activo', {}))
            if not esta_activo:
                return {
                    'valido': False,
                    'mensaje': 'Licencia desactivada. Contacte al administrador.',
                    'dias_restantes': 0,
                    'hwid': self.hwid,
                    'razon': 'desactivada'
                }
            
            # Verificar fecha de vencimiento
            fecha_vencimiento_str = get_field_value(fields.get('fecha_vencimiento', {}))
            
            if fecha_vencimiento_str:
                # Convertir timestamp de Firestore a datetime
                fecha_vencimiento = datetime.fromisoformat(fecha_vencimiento_str.replace('Z', '+00:00'))
                fecha_actual = datetime.now(fecha_vencimiento.tzinfo) if fecha_vencimiento.tzinfo else datetime.now()
                
                # Verificar si está vencida
                if fecha_actual > fecha_vencimiento:
                    return {
                        'valido': False,
                        'mensaje': 'Suscripción expirada. Renueve su licencia.',
                        'dias_restantes': 0,
                        'hwid': self.hwid,
                        'razon': 'vencida',
                        'fecha_vencimiento': fecha_vencimiento.strftime('%d/%m/%Y')
                    }
                
                # Calcular días restantes
                dias_restantes = (fecha_vencimiento - fecha_actual).days
                
                return {
                    'valido': True,
                    'mensaje': f'Licencia válida. {dias_restantes} días restantes.',
                    'dias_restantes': dias_restantes,
                    'hwid': self.hwid,
                    'razon': 'valida',
                    'fecha_vencimiento': fecha_vencimiento.strftime('%d/%m/%Y'),
                    'cliente': get_field_value(fields.get('cliente', {})) or 'N/A'
                }
            else:
                # Si no hay fecha de vencimiento, considerar licencia permanente
                return {
                    'valido': True,
                    'mensaje': 'Licencia válida (Permanente).',
                    'dias_restantes': -1,
                    'hwid': self.hwid,
                    'razon': 'permanente',
                    'cliente': get_field_value(fields.get('cliente', {})) or 'N/A'
                }
        
        except Exception as e:
            return {
                'valido': False,
                'mensaje': f'Error al validar licencia: {str(e)}',
                'dias_restantes': 0,
                'hwid': self.hwid,
                'razon': 'error'
            }
    
    def _mostrar_error_configuracion(self, error):
        """Muestra ventana de error de configuración"""
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error de Configuración",
            f"Error al inicializar Firebase:\n\n{error}\n\n"
            f"Contacte al administrador del sistema."
        )
        root.destroy()
    
    def mostrar_ventana_bloqueo(self, resultado_validacion):
        """Muestra ventana de bloqueo cuando la validación falla"""
        ventana = tk.Tk()
        ventana.title("Acceso Bloqueado")
        ventana.geometry("500x300")
        ventana.resizable(False, False)
        
        # Centrar ventana
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (500 // 2)
        y = (ventana.winfo_screenheight() // 2) - (300 // 2)
        ventana.geometry(f"+{x}+{y}")
        
        # Frame principal
        frame = tk.Frame(ventana, bg="#f0f0f0", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = tk.Label(
            frame,
            text="⚠️ ACCESO BLOQUEADO",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#d32f2f"
        )
        titulo.pack(pady=(0, 15))
        
        # Mensaje
        mensaje = tk.Label(
            frame,
            text=resultado_validacion['mensaje'],
            font=("Arial", 11),
            bg="#f0f0f0",
            fg="#333333",
            wraplength=450
        )
        mensaje.pack(pady=(0, 20))
        
        # Frame para HWID
        hwid_frame = tk.Frame(frame, bg="#ffffff", relief=tk.SOLID, borderwidth=1)
        hwid_frame.pack(fill=tk.X, pady=(0, 10))
        
        hwid_label = tk.Label(
            hwid_frame,
            text="ID de esta PC:",
            font=("Arial", 9, "bold"),
            bg="#ffffff",
            fg="#666666"
        )
        hwid_label.pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        hwid_value = tk.Label(
            hwid_frame,
            text=resultado_validacion['hwid'],
            font=("Courier", 11, "bold"),
            bg="#ffffff",
            fg="#1976d2"
        )
        hwid_value.pack(anchor=tk.W, padx=10, pady=(0, 5))
        
        # Botón copiar HWID
        def copiar_hwid():
            ventana.clipboard_clear()
            ventana.clipboard_append(resultado_validacion['hwid'])
            btn_copiar.config(text="✓ Copiado")
            ventana.after(2000, lambda: btn_copiar.config(text="Copiar ID"))
        
        btn_copiar = tk.Button(
            hwid_frame,
            text="Copiar ID",
            command=copiar_hwid,
            bg="#1976d2",
            fg="white",
            font=("Arial", 9),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        )
        btn_copiar.pack(pady=5)
        
        # Instrucciones
        instrucciones = tk.Label(
            frame,
            text="Para activar esta computadora, envíe el ID mostrado arriba\nal administrador del sistema.",
            font=("Arial", 9, "italic"),
            bg="#f0f0f0",
            fg="#666666",
            justify=tk.CENTER
        )
        instrucciones.pack(pady=(10, 15))
        
        # Botón cerrar
        def cerrar():
            ventana.destroy()
            sys.exit(0)
        
        btn_cerrar = tk.Button(
            frame,
            text="Cerrar",
            command=cerrar,
            bg="#757575",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=8
        )
        btn_cerrar.pack()
        
        ventana.protocol("WM_DELETE_WINDOW", cerrar)
        ventana.mainloop()
    
    def mostrar_aviso_vencimiento(self, resultado_validacion):
        """Muestra ventana de aviso cuando quedan pocos días de licencia"""
        dias = resultado_validacion['dias_restantes']
        
        ventana = tk.Tk()
        ventana.title("Aviso de Licencia")
        ventana.geometry("450x280")
        ventana.resizable(False, False)
        
        # Centrar ventana
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (450 // 2)
        y = (ventana.winfo_screenheight() // 2) - (280 // 2)
        ventana.geometry(f"+{x}+{y}")
        
        # Frame principal
        frame = tk.Frame(ventana, bg="#fff3cd", padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Determinar color y mensaje según días restantes
        if dias <= 7:
            color_titulo = "#d32f2f"
            icono = "⚠️"
            titulo_texto = "LICENCIA POR VENCER"
        elif dias <= 15:
            color_titulo = "#f57c00"
            icono = "⚠️"
            titulo_texto = "AVISO DE VENCIMIENTO"
        else:
            color_titulo = "#ffa000"
            icono = "ℹ️"
            titulo_texto = "RECORDATORIO"
        
        # Título
        titulo = tk.Label(
            frame,
            text=f"{icono} {titulo_texto}",
            font=("Arial", 14, "bold"),
            bg="#fff3cd",
            fg=color_titulo
        )
        titulo.pack(pady=(0, 15))
        
        # Mensaje principal
        if dias == 1:
            msg_dias = "1 día"
        else:
            msg_dias = f"{dias} días"
            
        mensaje = tk.Label(
            frame,
            text=f"Su licencia vencerá en {msg_dias}",
            font=("Arial", 12, "bold"),
            bg="#fff3cd",
            fg="#333333"
        )
        mensaje.pack(pady=(0, 10))
        
        # Fecha de vencimiento
        if 'fecha_vencimiento' in resultado_validacion:
            fecha_label = tk.Label(
                frame,
                text=f"Fecha de vencimiento: {resultado_validacion['fecha_vencimiento']}",
                font=("Arial", 10),
                bg="#fff3cd",
                fg="#666666"
            )
            fecha_label.pack(pady=(0, 20))
        
        # Mensaje de acción
        accion = tk.Label(
            frame,
            text="Por favor, contacte al administrador del sistema\npara renovar su licencia antes del vencimiento.",
            font=("Arial", 9, "italic"),
            bg="#fff3cd",
            fg="#666666",
            justify=tk.CENTER
        )
        accion.pack(pady=(0, 20))
        
        # Botón Aceptar
        def cerrar():
            ventana.destroy()
        
        btn_aceptar = tk.Button(
            frame,
            text="Entendido",
            command=cerrar,
            bg="#ffa000",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=8
        )
        btn_aceptar.pack()
        
        ventana.protocol("WM_DELETE_WINDOW", cerrar)
        ventana.mainloop()


def validar_licencia_inicio():
    """
    Función principal para validar licencia al inicio de la aplicación
    
    Returns:
        dict: Resultado de la validación o None si falla
    """
    try:
        validador = ValidadorLicencias()
        resultado = validador.validar_licencia()
        
        if not resultado['valido']:
            # Mostrar ventana de bloqueo y cerrar aplicación
            validador.mostrar_ventana_bloqueo(resultado)
            return None
        else:
            # Licencia válida, mostrar información en consola
            print(f"✓ Licencia válida: {resultado['mensaje']}")
            
            # Mostrar aviso si quedan 30 días o menos
            if resultado['dias_restantes'] > 0 and resultado['dias_restantes'] <= 30:
                print(f"⚠️  Advertencia: La licencia vencerá en {resultado['dias_restantes']} días")
                validador.mostrar_aviso_vencimiento(resultado)
            
            return resultado
            
    except Exception as e:
        # Error crítico en la validación
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Error del Sistema de Licencias",
            f"No se pudo validar la licencia:\n\n{str(e)}\n\n"
            f"Contacte al soporte técnico."
        )
        root.destroy()
        sys.exit(1)


if __name__ == "__main__":
    # Test del módulo
    print("=== Test del Sistema de Licencias ===")
    print(f"Sistema Operativo: {platform.system()}")
    
    validador = ValidadorLicencias()
    print(f"HWID de esta PC: {validador.hwid}")
    
    resultado = validador.validar_licencia()
    print(f"\nResultado de validación:")
    print(f"  Válido: {resultado['valido']}")
    print(f"  Mensaje: {resultado['mensaje']}")
    print(f"  Días restantes: {resultado['dias_restantes']}")
    
    if not resultado['valido']:
        validador.mostrar_ventana_bloqueo(resultado)

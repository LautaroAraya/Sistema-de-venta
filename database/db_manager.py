import sqlite3
import os
import sys
from datetime import datetime
import hashlib

# Importar logger de errores
try:
    from utils.error_logger import log_exception, log_error
except ImportError:
    # Si no está disponible, crear funciones dummy
    def log_exception(e, context=None):
        pass
    def log_error(error_type, error_message, error_traceback=None, context=None, severity="ERROR"):
        pass

class DatabaseManager:
    def __init__(self, db_name='sistema_ventas.db'):
        # Obtener el directorio del script o del ejecutable
        if getattr(sys, 'frozen', False):
            # Si está empaquetado como exe
            self.base_path = os.path.dirname(sys.executable)
        else:
            # Si está en desarrollo
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.db_path = os.path.join(self.base_path, 'database', db_name)

        # Guardar fotos junto al ejecutable/script, en "fotos_reparaciones"
        self.fotos_path = os.path.join(self.base_path, 'fotos_reparaciones')
        os.makedirs(self.fotos_path, exist_ok=True)

        self.connection = None
        self.init_database()
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        try:
            if self.connection is None:
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
            return self.connection
        except Exception as e:
            log_exception(e, context={
                'modulo': 'DatabaseManager',
                'accion': 'get_connection',
                'db_path': self.db_path
            })
            raise
    
    def init_database(self):
        """Inicializar todas las tablas de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nombre_completo TEXT NOT NULL,
                rol TEXT NOT NULL CHECK(rol IN ('admin', 'empleado')),
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de categorías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT,
                activo INTEGER DEFAULT 1
            )
        ''')
        
        # Tabla de proveedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                contacto TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                activo INTEGER DEFAULT 1,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                categoria_id INTEGER,
                precio REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                proveedor_id INTEGER,
                activo INTEGER DEFAULT 1,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id),
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
            )
        ''')
        
        # Tabla de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_factura TEXT UNIQUE NOT NULL,
                usuario_id INTEGER NOT NULL,
                cliente_nombre TEXT,
                cliente_documento TEXT,
                subtotal REAL NOT NULL,
                descuento_total REAL DEFAULT 0,
                total REAL NOT NULL,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Tabla de detalles de venta
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                descuento_porcentaje REAL DEFAULT 0,
                descuento_monto REAL DEFAULT 0,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        ''')
        
        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                nombre_sistema TEXT DEFAULT 'SISTEMA DE VENTAS',
                logo_path TEXT,
                telefono TEXT,
                direccion TEXT,
                cuit TEXT,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de reparaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reparaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_orden TEXT UNIQUE NOT NULL,
                usuario_id INTEGER NOT NULL,
                cliente_nombre TEXT NOT NULL,
                cliente_telefono TEXT,
                cliente_email TEXT,
                dispositivo TEXT NOT NULL,
                modelo TEXT,
                numero_serie TEXT,
                problema TEXT NOT NULL,
                sin_bateria INTEGER DEFAULT 0,
                rajado INTEGER DEFAULT 0,
                mojado INTEGER DEFAULT 0,
                contrasena TEXT,
                patron TEXT,
                sena REAL DEFAULT 0,
                total REAL NOT NULL,
                estado TEXT NOT NULL CHECK(estado IN ('en_proceso', 'en_espera_retiro', 'retirado')),
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_entrega TIMESTAMP,
                fecha_pago_final TIMESTAMP,
                medio_pago_final TEXT,
                monto_pago_final REAL DEFAULT 0,
                recargo_tarjeta REAL DEFAULT 0,
                observaciones TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        # Tabla de ventas de celulares
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas_celulares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_venta TEXT UNIQUE NOT NULL,
                usuario_id INTEGER NOT NULL,
                cliente_nombre TEXT NOT NULL,
                cliente_documento TEXT,
                cliente_telefono TEXT,
                cliente_email TEXT,
                telefono_marca TEXT,
                telefono_modelo TEXT,
                descripcion TEXT,
                subtotal REAL DEFAULT 0,
                descuento REAL DEFAULT 0,
                total REAL NOT NULL,
                sena REAL DEFAULT 0,
                fecha_pago_final TIMESTAMP,
                medio_pago_final TEXT,
                monto_pago_final REAL DEFAULT 0,
                recargo_tarjeta REAL DEFAULT 0,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')
        
        conn.commit()
        
        # Actualizar estructura de tablas existentes
        self.actualizar_estructura_tablas()
        
        # Crear usuario admin por defecto si no existe
        self.crear_usuario_admin_default()
        
        # Crear configuración por defecto si no existe
        self.crear_configuracion_default()
    
    def actualizar_estructura_tablas(self):
        """Actualizar estructura de tablas existentes agregando columnas nuevas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Agregar tabla de movimientos de caja si no existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movimientos_caja'")
            if not cursor.fetchone():
                cursor.execute('''
                    CREATE TABLE movimientos_caja (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        caja_id INTEGER NOT NULL,
                        tipo TEXT NOT NULL CHECK(tipo IN ('efectivo', 'transferencia', 'tarjeta')),
                        monto REAL NOT NULL,
                        descripcion TEXT,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (caja_id) REFERENCES cajas (id)
                    )
                ''')
                conn.commit()
            
            # Agregar columna descripcion en ventas_celulares si no existe
            cursor.execute("PRAGMA table_info(ventas_celulares)")
            columnas = [info[1] for info in cursor.fetchall()]
            if 'descripcion' not in columnas:
                cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN descripcion TEXT")
                conn.commit()
            if 'fecha_pago_final' not in columnas:
                cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN fecha_pago_final TIMESTAMP")
                conn.commit()
            if 'medio_pago_final' not in columnas:
                cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN medio_pago_final TEXT")
                conn.commit()
            if 'monto_pago_final' not in columnas:
                cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN monto_pago_final REAL DEFAULT 0")
                conn.commit()
            if 'recargo_tarjeta' not in columnas:
                cursor.execute("ALTER TABLE ventas_celulares ADD COLUMN recargo_tarjeta REAL DEFAULT 0")
                conn.commit()

            # Verificar si la tabla reparaciones existe y hacer migración si es necesario
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='reparaciones'")
            table_def = cursor.fetchone()
            
            if table_def and 'pendiente' in table_def[0]:
                # La tabla tiene la restricción antigua, necesita migración
                # Crear tabla temporal con nueva estructura
                cursor.execute('''
                    CREATE TABLE reparaciones_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        numero_orden TEXT UNIQUE NOT NULL,
                        usuario_id INTEGER NOT NULL,
                        cliente_nombre TEXT NOT NULL,
                        cliente_telefono TEXT,
                        cliente_email TEXT,
                        dispositivo TEXT NOT NULL,
                        modelo TEXT,
                        numero_serie TEXT,
                        problema TEXT NOT NULL,
                        sin_bateria INTEGER DEFAULT 0,
                        rajado INTEGER DEFAULT 0,
                        mojado INTEGER DEFAULT 0,
                        contrasena TEXT,
                        patron TEXT,
                        sena REAL DEFAULT 0,
                        total REAL NOT NULL,
                        estado TEXT NOT NULL CHECK(estado IN ('en_proceso', 'en_espera_retiro', 'retirado')),
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_entrega TIMESTAMP,
                        observaciones TEXT,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )
                ''')
                
                # Copiar datos migrando estados
                cursor.execute('''
                    INSERT INTO reparaciones_new
                    SELECT id, numero_orden, usuario_id, cliente_nombre, cliente_telefono, cliente_email,
                           dispositivo, modelo, numero_serie, problema, sin_bateria, rajado, mojado,
                           contrasena, patron, sena, total,
                           CASE 
                               WHEN estado = 'pendiente' THEN 'en_proceso'
                               WHEN estado = 'completada' THEN 'en_espera_retiro'
                               WHEN estado = 'cancelada' THEN 'retirado'
                               ELSE 'en_proceso'
                           END as estado,
                           fecha_creacion, fecha_entrega, observaciones
                    FROM reparaciones
                ''')
                
                # Eliminar tabla antigua
                cursor.execute('DROP TABLE reparaciones')
                
                # Renombrar tabla nueva
                cursor.execute('ALTER TABLE reparaciones_new RENAME TO reparaciones')
                
                conn.commit()
                print("Migración de estados de reparaciones completada exitosamente")
        except Exception as e:
            print(f"Error en migración de estructura: {str(e)}")
            conn.rollback()
        
        # Verificar y agregar columnas a la tabla reparaciones si no existen
        cursor.execute("PRAGMA table_info(reparaciones)")
        columnas_existentes = [col[1] for col in cursor.fetchall()]
        
        columnas_nuevas = {
            'sin_bateria': 'INTEGER DEFAULT 0',
            'rajado': 'INTEGER DEFAULT 0',
            'mojado': 'INTEGER DEFAULT 0',
            'contrasena': 'TEXT',
            'patron': 'TEXT',
            'fotos_reparacion_id': 'INTEGER',
            'fecha_pago_final': 'TIMESTAMP',
            'medio_pago_final': 'TEXT',
            'monto_pago_final': 'REAL DEFAULT 0',
            'recargo_tarjeta': 'REAL DEFAULT 0'
        }
        
        for columna, tipo in columnas_nuevas.items():
            if columna not in columnas_existentes:
                try:
                    cursor.execute(f'ALTER TABLE reparaciones ADD COLUMN {columna} {tipo}')
                    conn.commit()
                except Exception as e:
                    print(f"Error al agregar columna {columna}: {e}")
    
    def crear_usuario_admin_default(self):
        """Crear usuario administrador por defecto"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO usuarios (username, password, nombre_completo, rol)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'Administrador', 'admin'))
            conn.commit()
    
    def crear_configuracion_default(self):
        """Crear configuración por defecto"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM configuracion")
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO configuracion (id, nombre_sistema)
                VALUES (1, 'SISTEMA DE VENTAS')
            ''')
            conn.commit()
    
    def close(self):
        """Cerrar conexión a la base de datos"""
        if self.connection:
            self.connection.close()
            self.connection = None

import sys

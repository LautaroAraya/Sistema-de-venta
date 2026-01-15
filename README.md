# Sistema de Ventas

Sistema completo de ventas con gestión de inventario, proveedores y reportes.

## Características

- ✅ **Autenticación de usuarios** (Admin y Empleado)
- ✅ **Facturación completa** con descuentos por producto
- ✅ **Gestión de productos** con stock y categorías
- ✅ **Gestión de proveedores**
- ✅ **Reportes de ventas** con filtros por fecha
- ✅ **Generación de facturas en PDF**
- ✅ **Base de datos SQLite** integrada
- ✅ **Interfaz gráfica** con Tkinter

## Requisitos

- Python 3.8 o superior
- Windows 7/10/11

## Instalación para Desarrollo

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
python main.py
```

## Credenciales por Defecto

- **Usuario:** admin
- **Contraseña:** admin123

## Generar Ejecutable

### Opción 1: Usando el script batch
```bash
build_exe.bat
```

### Opción 2: Manual con PyInstaller
```bash
pip install -r requirements.txt
pyinstaller --clean --onefile --windowed --name "SistemaVentas" main.py
```

El ejecutable se generará en la carpeta `dist/`

## Crear Instalador

1. Instalar [Inno Setup](https://jrsoftware.org/isinfo.php)

2. Abrir `installer_script.iss` con Inno Setup

3. Compilar el script (Build > Compile)

4. El instalador se generará en la carpeta `installer/`

## Estructura del Proyecto

```
Sistema de venta/
├── database/
│   ├── db_manager.py          # Gestor de base de datos
│   └── sistema_ventas.db      # Base de datos SQLite (se crea automáticamente)
├── models/
│   ├── usuario.py             # Modelo de usuarios
│   ├── producto.py            # Modelo de productos
│   ├── proveedor.py           # Modelo de proveedores
│   ├── categoria.py           # Modelo de categorías
│   └── venta.py               # Modelo de ventas
├── views/
│   ├── login_view.py          # Vista de login
│   ├── main_view.py           # Vista principal
│   ├── ventas_view.py         # Vista de facturación
│   ├── productos_view.py      # Vista de productos
│   ├── proveedores_view.py    # Vista de proveedores
│   ├── reportes_view.py       # Vista de reportes
│   └── usuarios_view.py       # Vista de usuarios (solo admin)
├── reports/                    # Carpeta para facturas PDF
├── main.py                     # Archivo principal
├── requirements.txt            # Dependencias
├── build_exe.bat              # Script para generar .exe
├── installer_script.iss       # Script de Inno Setup
└── README.md                   # Este archivo
```

## Uso del Sistema

### 1. Login
- Iniciar sesión con usuario y contraseña
- Dos roles: **Admin** (acceso completo) y **Empleado** (sin gestión de usuarios)

### 2. Nueva Venta/Factura
- Ingresar datos del cliente (opcional)
- Buscar productos por código o nombre
- Agregar productos con cantidad y descuento
- El sistema calcula automáticamente los totales
- Procesar venta y generar factura PDF

### 3. Gestión de Productos
- Crear, editar y eliminar productos
- Asignar categorías y proveedores
- Control de stock automático

### 4. Gestión de Proveedores
- Registrar información de proveedores
- Vincular productos a proveedores

### 5. Reportes
- Ver historial de ventas
- Filtrar por fechas
- Estadísticas de ventas
- Ver detalle de cada venta

### 6. Usuarios (Solo Admin)
- Crear nuevos usuarios
- Asignar roles (Admin/Empleado)
- Cambiar contraseñas

## Base de Datos

El sistema utiliza SQLite con las siguientes tablas:

- **usuarios** - Usuarios del sistema
- **categorias** - Categorías de productos
- **proveedores** - Proveedores
- **productos** - Inventario de productos
- **ventas** - Registro de ventas
- **detalles_venta** - Items de cada venta

La base de datos se crea automáticamente al iniciar el sistema por primera vez.

## Características Técnicas

- **Base de datos:** SQLite (sin servidor requerido)
- **Interfaz:** Tkinter (incluido en Python)
- **Generación PDF:** ReportLab
- **Empaquetado:** PyInstaller
- **Instalador:** Inno Setup

## Soporte

Para reportar problemas o sugerencias, contactar al desarrollador.

## Licencia

Este software es propietario. Todos los derechos reservados.

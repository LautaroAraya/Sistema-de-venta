# 📝 Sistema de Reporte de Errores - Documentación

## 🎯 Descripción

El sistema de reporte de errores registra automáticamente todos los errores que ocurren en la aplicación, permitiendo que los administradores puedan revisarlos y solucionarlos.

## 📂 Ubicación de los Logs

Los errores se guardan en:
```
Sistema de venta/
└── logs/
    └── errors/
        ├── error_log.txt          # Registro completo de errores
        ├── errores_resumen.json   # Resumen estadístico
        └── error_log_backup_*.txt # Backups automáticos
```

## 🔍 Características

### 1. Registro Automático de Errores
- **Captura automática**: Todos los errores no controlados se registran automáticamente
- **Información detallada**: Fecha, hora, tipo de error, mensaje, traceback completo
- **Contexto adicional**: Usuario, módulo, acción en la que ocurrió el error
- **Niveles de severidad**: ERROR, WARNING, CRITICAL

### 2. Panel de Administración (Solo Administradores)
Para acceder al panel de errores:
1. Inicia sesión como **Administrador**
2. En el menú lateral, haz clic en **🐛 Errores del Sistema**

### 3. Funcionalidades del Panel

#### Ver Errores
- Lista de todos los errores registrados
- Detalles completos de cada error
- Estadísticas resumidas (total de errores, último error)

#### Abrir Archivo de Log
- Abre el archivo `error_log.txt` con el editor predeterminado
- Útil para copiar o compartir información de errores

#### Limpiar Logs Antiguos
- Crea un backup automático antes de limpiar
- Resetea el contador de errores
- Mantiene el historial en backups con fecha

## 💻 Uso Programático

### Registrar Errores Manualmente

```python
from utils.error_logger import log_error, log_exception

# Registrar un error simple
log_error(
    error_type="ValidationError",
    error_message="El precio no puede ser negativo",
    context={
        'usuario': 'admin',
        'modulo': 'productos',
        'accion': 'crear_producto'
    },
    severity="WARNING"
)

# Registrar una excepción de Python
try:
    resultado = 10 / 0
except Exception as e:
    log_exception(e, context={
        'usuario': 'vendedor1',
        'modulo': 'ventas',
        'accion': 'calcular_total'
    })
```

### Obtener Información de Errores

```python
from utils.error_logger import get_error_logger

logger = get_error_logger()

# Obtener resumen
summary = logger.get_error_summary()
print(f"Total de errores: {summary['total_errores']}")

# Obtener errores recientes
recent_errors = logger.get_recent_errors(limit=10)
for error in recent_errors:
    print(error)
```

## 🔄 Buscar Actualizaciones

### Script de Búsqueda Automática

Para buscar nuevas versiones disponibles, ejecuta:

```bash
python buscar_actualizacion.py
```

Este script:
- ✅ Verifica la versión actual instalada
- ✅ Consulta GitHub por nuevas versiones
- ✅ Compara versiones automáticamente
- ✅ Descarga la actualización si está disponible
- ✅ Proporciona instrucciones de instalación

### Desde la Interfaz

El sistema verifica automáticamente cada 5 días si hay actualizaciones disponibles al iniciar.

## 📊 Formato del Log de Errores

```
================================================================================
[ERROR] 2026-01-16 14:30:45
Tipo: ValueError
Mensaje: El stock no puede ser negativo

Contexto:
  - usuario: admin
  - modulo: productos
  - accion: actualizar_stock

Traceback:
File "views/productos_view.py", line 156, in guardar_producto
    raise ValueError("El stock no puede ser negativo")
================================================================================
```

## 🛡️ Seguridad

- Solo los **administradores** pueden ver el registro de errores
- Los backups se crean automáticamente antes de limpiar logs
- Los archivos de log están en la carpeta local, no se envían automáticamente

## ⚙️ Configuración Avanzada

### Cambiar Ubicación de Logs

Modifica en `utils/error_logger.py`:

```python
self.errors_dir = os.path.join(base_path, "logs", "errors")
```

### Personalizar Retención de Logs

Por defecto, los logs se mantienen hasta que el administrador los limpie manualmente. Para limpiar automáticamente:

```python
logger = get_error_logger()
logger.clear_old_errors(days=30)  # Limpiar logs de más de 30 días
```

## 📝 Ejemplos de Uso

### Ejemplo 1: Capturar Error en Vista
```python
def guardar_venta(self):
    try:
        # Código de la venta
        self.venta_model.guardar(datos)
    except Exception as e:
        log_exception(e, context={
            'usuario': self.user_data.get('usuario'),
            'vista': 'VentasView',
            'accion': 'guardar_venta'
        })
        messagebox.showerror("Error", "No se pudo guardar la venta")
```

### Ejemplo 2: Registrar Advertencia
```python
if stock < stock_minimo:
    log_error(
        error_type="StockWarning",
        error_message=f"Stock bajo: {producto} tiene {stock} unidades",
        context={'producto_id': producto_id},
        severity="WARNING"
    )
```

## 🚀 Mejores Prácticas

1. **Siempre proporciona contexto**: Incluye usuario, módulo y acción
2. **Usa severidad apropiada**:
   - `WARNING`: Situaciones que no impiden la operación
   - `ERROR`: Errores recuperables
   - `CRITICAL`: Errores que afectan funcionalidad principal

3. **Revisa logs regularmente**: Como administrador, revisa el panel de errores periódicamente
4. **Mantén backups**: Antes de limpiar logs, verifica que se creó el backup
5. **No registres información sensible**: Evita registrar contraseñas o datos personales

## 🔧 Solución de Problemas

### No se crean los archivos de log
- Verifica permisos de escritura en la carpeta del proyecto
- Asegúrate de que existe la carpeta `logs/errors/`

### No puedo ver el panel de errores
- Verifica que iniciaste sesión como **Administrador**
- El botón solo aparece en el menú para usuarios con rol admin

### Los errores no se registran automáticamente
- Verifica que la integración en `main.py` está correcta
- Comprueba que el `sys.excepthook` está configurado

## 📞 Soporte

Si encuentras problemas con el sistema de errores, revisa:
1. El archivo `error_log.txt` para detalles técnicos
2. La consola/terminal para mensajes de error
3. Los permisos de archivos y carpetas

---

**Versión**: 1.0.0  
**Última actualización**: Enero 2026

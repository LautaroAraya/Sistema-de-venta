# Reparaciones en Reportes - Cambios Implementados

## Resumen
Se agregó la funcionalidad para que las **reparaciones aparezcan en los reportes** con sus propias estadísticas y detalles. Los cambios se sincronizan automáticamente cuando actualizas el precio de una reparación.

## Cambios Realizados

### 1. **Reportes con Pestañas** 
Se transformó la vista de reportes a un sistema de pestañas:
- **Pestaña "💰 Ventas"** - Reportes de ventas (existente)
- **Pestaña "🔧 Reparaciones"** - Nuevo: Reportes de reparaciones

### 2. **Reportes de Reparaciones - Características**

#### Filtros Disponibles:
- **Rango de fechas**: Desde y Hasta (YYYY-MM-DD)
- **Por Estado**: Pendiente, En Proceso, Completada, Cancelada
- **Atajos**: Hoy, Este Mes
- **Botón Limpiar**: Limpia todos los filtros

#### Estadísticas en Tiempo Real:
- **Total de Reparaciones**: Cantidad filtrada
- **Total Ingresos**: Suma de todos los totales (solo reparaciones completadas o en proceso)
- **Total Seña**: Suma de todas las señas cobradas
- **Promedio por Reparación**: Ingreso promedio

#### Tabla de Reparaciones:
| Columna | Descripción |
|---------|-------------|
| N° Orden | Número único REP-YYYYMMDD-XXXX |
| Cliente | Nombre del cliente |
| Dispositivo | Tipo de dispositivo |
| Estado | Pendiente, En Proceso, Completada, Cancelada |
| Seña | Cantidad cobrada como seña |
| Total | Precio total de la reparación |
| Fecha | Fecha de creación |

#### Opciones de Visualización:
- **Ver Detalles**: Abre una ventana con toda la información de la reparación
- Actualización automática cuando editas una reparación

### 3. **Sincronización de Precios**

Cuando actualizas el precio de una reparación desde la sección "Reparaciones":
1. Los cambios se guardan en la base de datos
2. Los reportes se actualizan automáticamente la próxima vez que:
   - Cambias de pestaña
   - Aplicas nuevos filtros
   - Recargas la aplicación

**Nota**: Los reportes muestran los datos actuales sin necesidad de actualización manual.

### 4. **Detalles de Reparación**

Al hacer clic en "Ver Detalles de Reparación", se abre un diálogo con:
- Información del cliente (nombre, teléfono, email)
- Datos del dispositivo (tipo, modelo, número de serie)
- Problema reportado
- Observaciones técnicas
- Precios (seña y total)
- Estado actual
- Fecha de creación

## Cómo Usar

### Ver Reportes de Reparaciones:
1. Abre la aplicación
2. Ve a **📊 Reportes**
3. Haz clic en la pestaña **🔧 Reparaciones**
4. (Opcional) Aplica filtros:
   - Selecciona rango de fechas
   - Elige estado específico
   - Haz clic en "Aplicar"

### Actualizar Precio de una Reparación:
1. Ve a **🔧 Reparaciones** (en el menú principal)
2. Busca y selecciona la reparación
3. Edítala y cambia el precio
4. Guarda los cambios
5. Los reportes se actualizarán automáticamente

## Estructura de Datos

Las reparaciones en reportes muestran:
- Información desde la tabla `reparaciones`
- Totales calculados automáticamente
- Estados convertidos a formato legible
- Fechas formateadas (YYYY-MM-DD)

## Notas Técnicas

- Las estadísticas se calculan en tiempo real basándose en el filtro actual
- Los cambios en precios se reflejan inmediatamente en los reportes
- El sistema maneja correctamente valores NULL y formatos de moneda
- Soporta múltiples monedas y formatos de precio

## Archivos Modificados

- `views/reportes_view.py` - Completa reescritura con sistema de pestañas

## Compatibilidad

✅ Funciona con todas las funciones existentes de reparaciones  
✅ No afecta la funcionalidad de ventas  
✅ Compatible con exportación de reportes (si se implementa)  
✅ Funciona en cualquier computadora (usa rutas relativas correctas)

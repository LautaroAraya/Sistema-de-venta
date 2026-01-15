# MANUAL DE USO - SISTEMA DE VENTAS

## INSTALACIÓN

### Para Usuarios Finales (Instalador)
1. Ejecutar `SistemaVentas_Setup.exe`
2. Seguir las instrucciones del instalador
3. El sistema se instalará en `C:\Program Files\Sistema de Ventas`
4. Se creará un acceso directo en el escritorio y menú inicio
5. Ejecutar el sistema desde el acceso directo

### Para Desarrollo
1. Tener instalado Python 3.8 o superior
2. Abrir terminal en la carpeta del proyecto
3. Ejecutar: `pip install -r requirements.txt`
4. Ejecutar: `python inicializar_datos.py` (primera vez)
5. Ejecutar: `python main.py`

O simplemente ejecutar `run.bat`

---

## PRIMER USO

### Credenciales por Defecto
- **Administrador:**
  - Usuario: `admin`
  - Contraseña: `admin123`

- **Empleado (ejemplo):**
  - Usuario: `empleado1`
  - Contraseña: `empleado123`

⚠️ **IMPORTANTE:** Cambiar las contraseñas después del primer login.

---

## GUÍA DE USO

### 1. LOGIN
1. Ingresar usuario y contraseña
2. Presionar "Iniciar Sesión" o Enter
3. El sistema validará las credenciales

### 2. INTERFAZ PRINCIPAL

#### Menú Lateral (disponible para todos)
- **Nueva Venta:** Módulo de facturación
- **Productos:** Gestión del inventario
- **Proveedores:** Gestión de proveedores
- **Reportes:** Historial y estadísticas de ventas
- **Usuarios:** Gestión de usuarios (SOLO ADMIN)

#### Barra Superior
- Muestra el usuario actual y su rol
- Botón "Cerrar Sesión"

---

### 3. NUEVA VENTA / FACTURACIÓN

#### Proceso de Venta:

1. **Datos del Cliente (Opcional)**
   - Nombre del cliente
   - Documento de identidad
   - Si no se ingresa, se asigna "Cliente Genérico"

2. **Buscar Producto**
   - Escribir código o nombre del producto
   - Los resultados aparecen automáticamente
   - Click en el producto deseado

3. **Configurar Item**
   - Verificar precio y stock
   - Ingresar cantidad deseada
   - Ingresar descuento % (si aplica)
   - Click en "Agregar a la Venta"

4. **Agregar Más Productos**
   - Repetir pasos 2 y 3 para cada producto
   - Los items se van agregando a la tabla
   - El total se calcula automáticamente

5. **Revisar Venta**
   - Verificar todos los items en la tabla
   - Verificar totales (Subtotal, Descuento, Total)
   - Para eliminar un item: seleccionarlo y click en "Eliminar Item Seleccionado"

6. **Procesar Venta**
   - Click en "Procesar Venta"
   - Confirmar la operación
   - Se generará un número de factura automáticamente
   - Opción de generar PDF de la factura

7. **Cancelar Venta**
   - Click en "Cancelar / Nueva Venta"
   - Confirmar cancelación
   - Se limpiará toda la información

#### Ejemplo de Venta:
```
Cliente: Juan Pérez
Documento: 12345678

Productos:
- Hamburguesa Doble x2 = $15.00 (10% desc = $13.50)
- Coca Cola 500ml x2 = $5.00
- Papas Fritas Grandes x1 = $3.50

Subtotal: $23.50
Descuento: $1.50
TOTAL: $22.00
```

---

### 4. GESTIÓN DE PRODUCTOS

#### Listar Productos
- Se muestran todos los productos activos
- Información visible: Código, Nombre, Categoría, Precio, Stock, Proveedor

#### Nuevo Producto
1. Click en "Nuevo Producto"
2. Completar información:
   - **Código:** Único, ej: "BEB001"
   - **Nombre:** Descriptivo
   - **Descripción:** Opcional
   - **Categoría:** Seleccionar de la lista
   - **Precio:** Precio de venta
   - **Stock:** Cantidad inicial
   - **Proveedor:** Seleccionar de la lista
3. Click en "Guardar"

#### Editar Producto
1. Seleccionar producto en la tabla
2. Click en "Editar"
3. Modificar información
4. Click en "Guardar"

#### Eliminar Producto
1. Seleccionar producto en la tabla
2. Click en "Eliminar"
3. Confirmar eliminación
4. El producto se desactiva (no se borra)

⚠️ **Nota:** El stock se actualiza automáticamente con cada venta.

---

### 5. GESTIÓN DE PROVEEDORES

#### Nuevo Proveedor
1. Click en "Nuevo Proveedor"
2. Completar información:
   - **Nombre:** Nombre de la empresa (obligatorio)
   - **Contacto:** Nombre del contacto
   - **Teléfono:** Número de contacto
   - **Email:** Correo electrónico
   - **Dirección:** Dirección física
3. Click en "Guardar"

#### Editar/Eliminar
- Similar al proceso de productos

---

### 6. REPORTES DE VENTAS

#### Filtros Disponibles
- **Por Fecha:** Desde - Hasta (formato: YYYY-MM-DD)
- **Filtros Rápidos:**
  - Hoy
  - Esta Semana
  - Este Mes
  - Limpiar (ver todas)

#### Estadísticas
- Total de ventas (cantidad)
- Total ingresos ($)
- Promedio por venta ($)

#### Ver Detalles de Venta
1. Seleccionar venta en la tabla
2. Click en "Ver Detalles de Venta"
3. Se muestra:
   - Información de la factura
   - Cliente
   - Vendedor
   - Todos los productos vendidos
   - Totales

---

### 7. GESTIÓN DE USUARIOS (SOLO ADMIN)

#### Crear Usuario
1. Click en "Nuevo Usuario"
2. Completar información:
   - **Usuario:** Nombre de usuario único
   - **Nombre Completo:** Nombre real del usuario
   - **Contraseña:** Mínimo 6 caracteres
   - **Confirmar:** Repetir contraseña
   - **Rol:** Admin o Empleado
3. Click en "Guardar"

#### Cambiar Contraseña
1. Seleccionar usuario
2. Click en "Cambiar Contraseña"
3. Ingresar nueva contraseña
4. Confirmar contraseña
5. Click en "Guardar"

#### Diferencias entre Roles:
- **Admin:** Acceso completo al sistema
- **Empleado:** No puede gestionar usuarios

---

## GENERACIÓN DE FACTURAS PDF

Las facturas se generan automáticamente en formato PDF después de procesar una venta.

**Ubicación:**
- Desarrollo: `carpeta_proyecto/reports/`
- Instalado: `C:\Program Files\Sistema de Ventas\reports\`

**Nombre:** `FAC-YYYYMMDD-XXXX.pdf`

**Contenido:**
- Número de factura
- Fecha y hora
- Datos del vendedor
- Datos del cliente
- Detalle de productos
- Totales

---

## RESPALDO DE DATOS

### Base de Datos
La base de datos se encuentra en:
- Desarrollo: `carpeta_proyecto/database/sistema_ventas.db`
- Instalado: `C:\Program Files\Sistema de Ventas\database\sistema_ventas.db`

### Hacer Respaldo
1. Copiar el archivo `sistema_ventas.db`
2. Guardarlo en un lugar seguro
3. Incluir la fecha en el nombre: `sistema_ventas_2026-01-15.db`

### Restaurar Respaldo
1. Cerrar el sistema
2. Reemplazar `sistema_ventas.db` con el respaldo
3. Reiniciar el sistema

⚠️ **RECOMENDACIÓN:** Hacer respaldos diarios de la base de datos.

---

## SOLUCIÓN DE PROBLEMAS

### "Usuario o contraseña incorrectos"
- Verificar mayúsculas/minúsculas
- Si olvidó la contraseña de admin, contactar soporte

### "Stock insuficiente"
- Verificar stock disponible del producto
- Actualizar stock en Gestión de Productos

### "Error al crear venta"
- Verificar que todos los productos tengan stock
- Reiniciar el sistema
- Verificar integridad de la base de datos

### La aplicación no inicia
- Verificar que Python esté instalado (desarrollo)
- Reinstalar la aplicación (instalador)
- Revisar logs de errores

### Facturas no se generan
- Verificar permisos de escritura en carpeta `reports`
- Verificar que ReportLab esté instalado

---

## ATAJOS DE TECLADO

- **Enter:** Aceptar/Continuar
- **Esc:** Cancelar (en diálogos)
- **Tab:** Navegar entre campos

---

## CONSEJOS Y MEJORES PRÁCTICAS

1. **Seguridad:**
   - Cambiar contraseñas por defecto
   - Usar contraseñas seguras (min. 8 caracteres)
   - Cerrar sesión al terminar

2. **Inventario:**
   - Actualizar stock regularmente
   - Revisar productos con stock bajo
   - Mantener códigos de producto consistentes

3. **Ventas:**
   - Siempre verificar totales antes de procesar
   - Guardar facturas PDF importantes
   - Revisar reportes diariamente

4. **Respaldos:**
   - Hacer respaldos diarios de la base de datos
   - Guardar respaldos en múltiples ubicaciones
   - Probar restaurar respaldos periódicamente

5. **Rendimiento:**
   - Cerrar el sistema correctamente
   - No eliminar archivos de la carpeta de instalación
   - Reiniciar el sistema si presenta lentitud

---

## SOPORTE TÉCNICO

Para asistencia técnica, contactar a:
- Email: soporte@sistemadeventas.com
- Teléfono: (555) 1234-5678
- Horario: Lunes a Viernes, 9:00 - 18:00

---

## ACTUALIZACIONES

Para actualizar el sistema:
1. Hacer respaldo de la base de datos
2. Desinstalar versión anterior
3. Instalar nueva versión
4. Restaurar base de datos si es necesario

⚠️ La base de datos es compatible entre versiones.

---

**Versión del Manual:** 1.0
**Fecha:** Enero 2026
**Sistema:** Sistema de Ventas v1.0

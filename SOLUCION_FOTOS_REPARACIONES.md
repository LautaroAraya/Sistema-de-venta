# Solución: Fotos no se muestran al editar reparaciones en otra computadora

## Problema
Cuando instalas la aplicación en otra computadora, al intentar editar una reparación existente, las fotos cargadas no aparecen.

## Causa
El problema estaba en las **rutas de archivos no portables**:
- Las fotos se guardaban usando `os.getcwd()` (directorio actual), que puede variar según donde se ejecute la aplicación
- En otra computadora, el directorio actual es diferente, por lo que las fotos no se encuentran
- Esto afectaba especialmente cuando:
  - La carpeta `fotos_reparaciones` estaba en la ubicación equivocada
  - El archivo `.exe` se ejecutaba desde una ubicación diferente a donde se copió la aplicación

## Soluciones implementadas

### 1. **Rutas absolutas y consistentes**
Las fotos ahora se guardan siempre en:
```
<raíz_aplicación>/fotos_reparaciones/ticket_REP-YYYYMMDD-XXXX/
```

Se usó `self.db_manager.fotos_path` en lugar de `os.getcwd()` para garantizar consistencia.

**Archivos modificados:**
- `views/reparacion_view.py` (líneas 720 y 765)
- `models/reparacion.py` (función `obtener_fotos`)

### 2. **Validación de archivos**
Se añadió validación para verificar que los archivos realmente existan antes de intentar cargarlos:

```python
# En cargar_fotos_reparacion
fotos = self.reparacion_model.obtener_fotos(reparacion_id)
self.fotos_actuales = [foto for foto in fotos if os.path.exists(foto)]
```

### 3. **Manejo mejorado de errores**
Se mejoró el manejo de casos donde un archivo no existe, mostrando un aviso en lugar de fallar silenciosamente.

## Pasos para resolver el problema en tu instalación

### Opción A: Migrar fotos automáticamente
Si ya has instalado la aplicación en otra computadora y tienes fotos guardadas:

1. Ejecuta el script de migración:
   ```bash
   python migrar_fotos_reparaciones.py
   ```

2. Este script:
   - Busca fotos en ubicaciones antiguas
   - Las mueve automáticamente a la ubicación correcta
   - Muestra un resumen de lo que hizo

### Opción B: Manual (si la opción A no funciona)
1. Localiza dónde está el archivo `.exe` de tu aplicación
2. Asegúrate de que haya una carpeta `fotos_reparaciones` en ese mismo directorio
3. Las fotos deben estar organizadas como:
   ```
   fotos_reparaciones/
   ├── ticket_REP-20260101-0001/
   │   ├── foto_01.jpg
   │   ├── foto_02.jpg
   │   └── ...
   ├── ticket_REP-20260102-0002/
   │   └── ...
   ```

### Opción C: Copiar carpeta de fotos
Si instalaste en otra computadora y quieres copiar las fotos:

1. En la computadora original, copia la carpeta `fotos_reparaciones`
2. En la nueva computadora, pégala en el mismo directorio donde está el archivo `.exe` o la carpeta de la aplicación

## Cómo garantizar que no ocurra nuevamente

✅ **La aplicación ahora:**
- Guarda todas las fotos en la ubicación consistente usando `db_manager.fotos_path`
- Valida que los archivos existan antes de mostrarlos
- Es portable entre diferentes computadoras
- Funciona correctamente aunque se ejecute desde diferentes directorios

## Verificación
Para confirmar que todo funciona:

1. Crea una nueva reparación con fotos
2. Cierra la aplicación
3. Vuelve a abrirla
4. Busca la reparación y edítala
5. Las fotos deberían aparecer en el apartado de galería

Si aún tienes problemas, revisa que la carpeta `fotos_reparaciones` esté en la ubicación correcta y contenga las fotos organizadas por ticket.

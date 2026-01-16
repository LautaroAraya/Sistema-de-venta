# 🔄 GUÍA DE ACTUALIZACIONES DEL SISTEMA

## 📋 Índice
1. [Cómo funciona el sistema](#cómo-funciona)
2. [Crear una actualización](#crear-actualización)
3. [Probar el sistema](#probar-el-sistema)
4. [Solución de problemas](#solución-de-problemas)

---

## 🔧 Cómo funciona el sistema

### Componentes del Sistema de Actualizaciones

1. **version.txt**: Archivo que contiene la versión actual (ej: 1.0.0)
2. **UpdateManager**: Clase que maneja la búsqueda e instalación de actualizaciones
3. **GitHub Releases**: Se utiliza GitHub Releases para publicar nuevas versiones
4. **crear_actualizacion.py**: Script para automatizar la creación de versiones

### Flujo de Actualización

```
Usuario presiona "Buscar Actualizaciones"
          ↓
Sistema consulta GitHub API
          ↓
¿Hay nueva versión?
    ├── SÍ → Muestra detalles y pregunta si desea instalar
    └── NO → Muestra "Versión actualizada"
          ↓
Si acepta instalar:
    1. Descarga archivos modificados (incremental)
    2. Si falla, descarga ZIP completo (fallback)
    3. Actualiza archivos (excepto database/)
    4. Actualiza version.txt
    5. Reinicia la aplicación
```

---

## 🚀 Crear una Actualización

### Método 1: Script Automático (Recomendado)

```bash
python crear_actualizacion.py
```

El script te guiará paso a paso:
1. Muestra la versión actual
2. Te pide la nueva versión (ej: 1.0.1)
3. Te pide una descripción de cambios
4. Hace commit, crea tag y sube a GitHub
5. Te indica que debes crear el Release en GitHub

### Método 2: Manual

```bash
# 1. Actualizar version.txt
echo "1.0.1" > version.txt

# 2. Hacer commit
git add .
git commit -m "v1.0.1: Descripción de cambios"

# 3. Crear tag
git tag v1.0.1

# 4. Subir a GitHub
git push origin main
git push origin v1.0.1

# 5. Crear Release en GitHub
# Ve a: https://github.com/LautaroAraya/Sistema-de-venta/releases
# Click en "Create a new release"
# - Tag: v1.0.1
# - Título: v1.0.1 - Nombre descriptivo
# - Descripción: Detalles de los cambios
# - Click en "Publish release"
```

---

## ✅ Probar el Sistema

### Prueba 1: Verificar que NO haya actualizaciones

**Escenario**: No has publicado ningún release en GitHub

1. Abre el sistema
2. Ve a **Configuración → Actualizaciones**
3. Click en **"Buscar Actualizaciones"**
4. **Resultado esperado**: 
   - Mensaje: "No hay releases publicados en GitHub todavía"
   - O: "Ya tienes la versión más reciente (v1.0.0)"

### Prueba 2: Crear y detectar actualización

**Escenario**: Crear una nueva versión para probar el flujo completo

#### Paso 1: Crear la actualización
```bash
# Ejecutar el script
python crear_actualizacion.py

# Ingresar datos:
# - Nueva versión: 1.0.1
# - Descripción: Prueba de actualización automática
```

#### Paso 2: Crear Release en GitHub
1. Ve a: https://github.com/LautaroAraya/Sistema-de-venta/releases
2. Click en **"Create a new release"**
3. Completa:
   - **Tag**: v1.0.1 (seleccionar del dropdown)
   - **Título**: v1.0.1 - Prueba de actualización
   - **Descripción**: 
     ```
     ## Cambios en esta versión
     - Mejoras en el sistema de actualizaciones
     - Correcciones de bugs
     - Prueba del flujo automático
     ```
4. Click en **"Publish release"**

#### Paso 3: Probar la detección
1. **Importante**: Asegúrate de que tu `version.txt` local diga `1.0.0`
   ```bash
   echo "1.0.0" > version.txt
   ```
2. Abre el sistema
3. Ve a **Configuración → Actualizaciones**
4. Click en **"Buscar Actualizaciones"**

#### Paso 4: Verificar resultados
**Resultado esperado**:
- ✅ Estado: "✓ Actualización disponible: v1.0.1"
- ✅ Aparece diálogo con:
  - Versión nueva: v1.0.1
  - Versión actual: v1.0.0
  - Notas de la actualización
  - Pregunta si desea instalar

#### Paso 5: Instalar actualización
1. Click en **"Sí"** en el diálogo
2. **Resultado esperado**:
   - Estado: "Instalando actualización..."
   - Descarga archivos
   - Mensaje: "Actualización Exitosa"
   - La aplicación se reinicia automáticamente
   - Después del reinicio, `version.txt` debe decir `1.0.1`

### Prueba 3: Verificar actualización incremental

**Escenario**: Modificar solo un archivo y verificar que solo se descargue ese archivo

1. Modificar `README.md`:
   ```bash
   echo "# Cambio de prueba" >> README.md
   git add README.md
   git commit -m "v1.0.2: Test actualización incremental"
   git tag v1.0.2
   git push origin main
   git push origin v1.0.2
   ```
2. Crear Release v1.0.2 en GitHub
3. Cambiar local a v1.0.1: `echo "1.0.1" > version.txt`
4. Buscar actualizaciones en el sistema
5. Instalar
6. **Resultado esperado**: Solo se descarga README.md (más rápido)

---

## 🔍 Solución de Problemas

### Error: "No se pudo conectar a GitHub"

**Causa**: Sin conexión a Internet o firewall bloqueando

**Solución**:
1. Verificar conexión a Internet
2. Probar acceder a: https://github.com/LautaroAraya/Sistema-de-venta
3. Verificar que no haya firewall bloqueando Python

### Error: "No hay releases publicados"

**Causa**: No has creado ningún Release en GitHub

**Solución**:
1. Ve a GitHub Releases
2. Crea un Release con un tag (ej: v1.0.0)
3. Publica el Release
4. Vuelve a buscar actualizaciones

### Error: "403 Forbidden" o "API rate limit"

**Causa**: GitHub limita las peticiones anónimas a 60 por hora

**Solución**:
1. Espera 1 hora
2. O configura un token de GitHub (avanzado)

### La actualización no se descarga

**Causa**: Error en la URL del release o permisos

**Verificar**:
1. El Release está marcado como público (no draft)
2. La versión en GitHub es mayor que la local
3. El repositorio es público

### Los archivos no se actualizan

**Causa**: Rutas protegidas o errores de escritura

**Verificar**:
1. El sistema NO actualiza: `database/`, `build/`, `dist/`, `installer/`
2. Cerrar el programa completamente antes de actualizar manualmente
3. Verificar permisos de escritura en la carpeta

### Error al reiniciar

**Causa**: No se puede ejecutar el programa después de actualizar

**Solución manual**:
1. Cerrar el programa
2. Abrir nuevamente desde:
   - Python: `python main.py`
   - EXE: Doble click en el ejecutable

---

## 📝 Checklist de Verificación

Antes de publicar una actualización:

- [ ] `version.txt` actualizado con nueva versión
- [ ] Commit realizado con descripción clara
- [ ] Tag creado (ej: v1.0.1)
- [ ] Tag subido a GitHub
- [ ] Release creado en GitHub con:
  - [ ] Tag correcto
  - [ ] Título descriptivo
  - [ ] Notas de la versión completas
  - [ ] Estado: Published (no Draft)
- [ ] Probado el flujo completo de actualización
- [ ] Verificado que la base de datos NO se borra

---

## 🎯 Mejores Prácticas

### Versionado Semántico (SemVer)

Usa el formato: `MAJOR.MINOR.PATCH` (ej: 1.2.3)

- **MAJOR** (1.x.x): Cambios incompatibles con versiones anteriores
- **MINOR** (x.1.x): Nuevas funcionalidades compatibles
- **PATCH** (x.x.1): Correcciones de bugs

Ejemplos:
- `1.0.0` → `1.0.1`: Corrección de bug
- `1.0.1` → `1.1.0`: Nueva funcionalidad
- `1.1.0` → `2.0.0`: Cambio importante en estructura

### Notas de la Actualización

Estructura recomendada:

```markdown
## Novedades ✨
- Nueva funcionalidad X
- Mejora en Y

## Correcciones 🐛
- Arreglado error en Z
- Corregido problema con W

## Cambios técnicos 🔧
- Actualización de dependencias
- Optimización de rendimiento
```

### Frecuencia de Actualizaciones

- **Críticas (bugs graves)**: Inmediatamente
- **Mejoras importantes**: Semanalmente
- **Mejoras menores**: Mensualmente

---

## 🆘 Contacto y Soporte

Si encuentras problemas:

1. Revisa esta guía
2. Verifica los logs de error
3. Contacta al desarrollador
4. Reporta el issue en GitHub

---

**Última actualización**: Enero 2026  
**Versión del sistema**: 1.0.0

# 🚀 Guía de Distribución de Actualizaciones - Sistema de Ventas

**Versión:** 1.0.11  
**Fecha:** 16 de enero de 2026

## 📋 Tabla de Contenidos
1. [Flujo Automático de Actualización](#flujo-automático)
2. [Cómo Crear una Release en GitHub](#crear-release-github)
3. [Distribuir a Clientes](#distribuir-clientes)
4. [Verificación de Actualizaciones](#verificación)

---

## 🔄 Flujo Automático

El sistema ahora tiene actualizaciones automáticas integradas:

### En el Cliente:
1. El programa **detecta automáticamente** si hay una nueva versión disponible
2. Si encuentra una actualización **más nueva**, notifica al usuario
3. El usuario puede actualizar en cualquier momento
4. La descarga y reinstalación ocurre **automáticamente**
5. El programa se reinicia con la nueva versión

### En el Servidor (Tú):
1. Haces cambios en el código
2. Ejecutas el script de deploy automático
3. Subes la nueva versión a GitHub como "Release"
4. ¡Los clientes reciben la actualización automáticamente!

---

## 📱 Crear una Release en GitHub

### Opción A: Manual (Recomendado para versiones importantes)

1. **Ve a tu repositorio** en GitHub
   ```
   https://github.com/TuUsuario/Sistema-de-venta
   ```

2. **Click en "Releases"** (lado derecho de la página)

3. **Click en "Create a new release"** (botón azul)

4. **Completa los campos:**
   - **Tag version**: `v1.0.12` (usa el formato v.X.X.X)
   - **Release title**: `Versión 1.0.12 - Nuevas características`
   - **Description**: Escribe qué cambios trae la versión
   
   **Ejemplo de descripción:**
   ```markdown
   ## ✨ Nuevas Características
   - Nuevo sistema de reportes avanzados
   - Mejoras en velocidad de búsqueda
   - Corrección de errores de sincronización
   
   ## 🐛 Bugs Corregidos
   - Error al exportar reportes en PDF
   - Problema con actualizaciones automáticas
   
   ## 📦 Instalación
   Descarga `SistemaVentas_Setup.exe` e instala normalmente
   ```

5. **Sube el archivo ejecutable:**
   - **Click en "Attach binaries"**
   - **Selecciona**: `SistemaVentas_Setup.exe`
   
   Esto hace que los clientes descarguen el .exe directamente sin instalar.

6. **Click en "Publish release"**

---

### Opción B: Automático con Script (RECOMENDADO)

Voy a crear un script que haga todo automáticamente:

```bash
python crear_release_github.py
```

Copia el script que está en el repositorio y ejecútalo. Te pedirá:
- Número de versión nueva
- Descripción de cambios
- Automáticamente sube el ejecutable a GitHub

---

## 💻 Distribuir a Clientes

### Método 1: Instalador (Para primera instalación)

1. **Copia el archivo**: `installer/SistemaVentas_Setup.exe`
2. **Envía al cliente** por email, Dropbox, Google Drive, etc.
3. **Cliente ejecuta el .exe** y sigue el instalador
4. **¡Listo!** El cliente tiene el sistema instalado

### Método 2: Actualización Automática (Para clientes que ya tienen instalado)

1. **Crea una release en GitHub** (ver arriba)
2. **Los clientes reciben notificación automáticamente**
3. **Ellos aceptan la actualización**
4. **Se descarga e instala automáticamente**
5. **El programa se reinicia con la nueva versión**

---

## ✅ Verificación de Actualizaciones

### Cliente verifica manualmente:

1. **Inicia sesión** en el programa
2. **Busca el botón** "⬇️ Buscar Actualizaciones" en el menú
3. **El programa verifica** automáticamente
4. Si hay actualizaciones, le pregunta si quiere descargar
5. Descarga e instala automáticamente

### Verificación automática:

El programa **verifica automáticamente cada 5 días**:
- Si hay una versión nueva disponible, notifica al usuario
- Si el usuario acepta, descarga e instala

---

## 🔍 Cómo Funciona Internamente

### Secuencia de descarga:

1. **Detecta versión nueva** en GitHub releases
2. **Intenta descargar el .exe compilado** (más rápido)
   - Si falta, cae a plan B
3. **Plan B: Descarga archivos modificados** individualmente
   - Solo descarga lo que cambió (más eficiente)
4. **Plan C: Descarga ZIP completo** como último recurso
   - Descomprime y reemplaza archivos

Esta estrategia garantiza:
- ⚡ **Actualizaciones rápidas** (solo descarga lo necesario)
- 🔒 **Seguridad** (protege la base de datos)
- 🛡️ **Recuperación** (si falla, intenta otro método)

---

## 📊 Estadísticas y Monitoreo

### Archivos generados:

- **`.update_config.json`**: Guarda estado de actualizaciones
- **`version.txt`**: Versión actual instalada
- **`logs/errors/`**: Registra errores del sistema

### Ver versión instalada:

Cliente ve la versión en:
- **Arriba a la izquierda** donde dice "v1.0.11"
- **En el título de la ventana**

---

## 🚨 Troubleshooting

### "Error: No se puede conectar a GitHub"
- Cliente sin internet
- Firewall bloqueando GitHub
- Problema temporal de GitHub

### "Error: No se encontró la nueva versión"
- Asegúrate que creaste la release con tag `v1.0.X`
- Verifica que el archivo .exe está en "Assets"

### "El programa no se reinicia después de actualizar"
- Verifica que existe `restart.py`
- Ejecuta manualmente el programa

---

## 📝 Pasos Resumidos para Cada Actualización

### 1️⃣ Hacer cambios en el código
```
Edita los archivos necesarios (views/, models/, etc.)
```

### 2️⃣ Actualizar versión
```
Edita: version.txt
Cambia: 1.0.11 → 1.0.12
```

### 3️⃣ Generar nuevo executable
```
Ejecuta: deploy.bat
O: python deploy_actualizacion.py
```

### 4️⃣ Crear release en GitHub
```
1. Ve a: https://github.com/TuUsuario/Sistema-de-venta/releases
2. Click: "Create a new release"
3. Tag: v1.0.12
4. Sube: SistemaVentas_Setup.exe
5. Publica
```

### 5️⃣ Los clientes reciben actualización automáticamente ✅

---

## 🎯 Mejores Prácticas

✅ **Haz:**
- Actualiza `version.txt` ANTES de compilar
- Escribe notas claras en las releases
- Sube el ejecutable a GitHub releases
- Prueba la actualización en otra PC antes de lanzar

❌ **No hagas:**
- Cambiar versión después de compilar
- Olvidar subir el .exe a GitHub
- Compilar sobre código sin guardar cambios
- Modificar la base de datos en actualizaciones

---

**¿Necesitas ayuda?** Contacta al desarrollador Digital&Servicios


# 📢 Cómo Hacer una Actualización

Este documento explica cómo publicar una actualización en GitHub para que los usuarios puedan descargarla desde la aplicación.

## Pasos para Actualizar:

### 1. **Actualizar la versión en el archivo `version.txt`**
   - Abre el archivo `version.txt` en la raíz del proyecto
   - Cambia el número de versión (ej: `1.0.0` → `1.0.1`)
   - Guarda el archivo

### 2. **Hacer commit de los cambios**
   ```bash
   git add .
   git commit -m "v1.0.1: Descripción de cambios"
   ```

### 3. **Crear un Tag en Git**
   ```bash
   git tag v1.0.1
   ```

### 4. **Empujar cambios a GitHub**
   ```bash
   git push origin main
   git push origin v1.0.1
   ```

### 5. **Crear Release en GitHub**
   - Ve a tu repositorio en GitHub
   - Ve a **Releases** (o presiona "r" en el repo)
   - Presiona **"Create a new release"**
   - En **"Tag version"**, selecciona o escribe `v1.0.1`
   - En **"Release title"**, escribe el título (ej: "v1.0.1 - Mejoras de interfaz")
   - En **"Describe this release"**, escribe las notas de la actualización (qué cambió)
   - Presiona **"Publish release"**

## 6. **Los usuarios verán la actualización**
   - Dentro del programa → **Configuración** → **Actualizaciones**
   - Presiona **"Buscar Actualizaciones"**
   - El sistema detectará la nueva versión en GitHub
   - El usuario podrá instalarla con un clic

## ⚠️ Puntos Importantes:

- **El archivo `version.txt` DEBE coincidir con el tag** (sin la "v")
  - Si el tag es `v1.0.1`, el archivo debe contener `1.0.1`
  
- **Las notas de la versión aparecerán en el programa**
  - Usa el campo "Describe this release" para escribir qué cambió

- **Los datos de los usuarios NO se pierden**
  - Solo se actualizan archivos del código
  - La carpeta `database/` se preserva

- **La aplicación se reiniciará automáticamente**
  - Después de instalar la actualización

## 📝 Ejemplo de Notas de Actualización:

```
## Cambios en v1.0.1

- ✨ Nueva interfaz responsiva para todos los tamaños de pantalla
- 🔧 Corrección de bugs en ventas
- 📊 Mejora en reportes
- 🚀 Optimización de velocidad

## Instalación
Presiona "Aceptar" y la aplicación se actualizará automáticamente.
```

## 🔍 Verificar desde el Programa

1. Abre el programa
2. Ve a **Configuración** → **Actualizaciones**
3. Presiona **"Buscar Actualizaciones"**
4. Verás la nueva versión disponible
5. Presiona para descargar e instalar

¡Listo! 🎉

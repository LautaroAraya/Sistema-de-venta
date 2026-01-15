# GUÍA COMPLETA PARA GENERAR EL EJECUTABLE E INSTALADOR

## SISTEMA DE VENTAS - CONVERSIÓN A .EXE E INSTALADOR

---

## REQUISITOS PREVIOS

### Software Necesario:
1. **Python 3.8 o superior** - Descarga: https://www.python.org/downloads/
2. **PyInstaller** - Se instala con pip
3. **Inno Setup 6** (para el instalador) - Descarga: https://jrsoftware.org/isdl.php

---

## PASO 1: PREPARAR EL ENTORNO

### 1.1 Verificar Python
Abrir PowerShell o CMD y ejecutar:
```bash
python --version
```
Debe mostrar: `Python 3.x.x`

### 1.2 Instalar Dependencias
```bash
cd "c:\Users\lauty\OneDrive\Escritorio\Sistema de venta"
pip install -r requirements.txt
```

### 1.3 Probar el Sistema
```bash
python main.py
```

Si todo funciona correctamente, continuar al Paso 2.

---

## PASO 2: GENERAR EL EJECUTABLE (.EXE)

### Opción A: Usar el Script Automático (RECOMENDADO)

1. Hacer doble clic en `build_exe.bat`
2. Esperar a que termine el proceso (puede tardar 2-5 minutos)
3. El ejecutable estará en la carpeta `dist/SistemaVentas.exe`

### Opción B: Comando Manual

Abrir PowerShell/CMD en la carpeta del proyecto:

```bash
# Instalar PyInstaller si no está instalado
pip install pyinstaller

# Generar ejecutable con PyInstaller
pyinstaller --clean --onefile --windowed --name "SistemaVentas" ^
  --add-data "database;database" ^
  --add-data "reports;reports" ^
  --hidden-import=PIL._tkinter_finder ^
  main.py
```

**Parámetros explicados:**
- `--clean`: Limpia compilaciones anteriores
- `--onefile`: Genera un solo archivo .exe
- `--windowed`: Sin consola (solo interfaz gráfica)
- `--name "SistemaVentas"`: Nombre del ejecutable
- `--add-data`: Incluye carpetas necesarias
- `--hidden-import`: Importaciones que PyInstaller podría omitir

### Opción C: Usar el archivo .spec (Avanzado)

```bash
pyinstaller --clean sistema_ventas.spec
```

---

## PASO 3: PROBAR EL EJECUTABLE

1. Navegar a la carpeta `dist/`
2. Ejecutar `SistemaVentas.exe`
3. Verificar que:
   - Se abre el login
   - Se puede iniciar sesión
   - Todas las funcionalidades funcionan

**IMPORTANTE:** 
- La base de datos se creará en la misma carpeta del .exe
- Las facturas PDF se guardarán en `reports/` junto al .exe

---

## PASO 4: CREAR EL INSTALADOR CON INNO SETUP

### 4.1 Instalar Inno Setup
1. Descargar desde: https://jrsoftware.org/isdl.php
2. Instalar (siguiente, siguiente, finalizar)

### 4.2 Preparar Estructura
Asegurarse de tener:
```
Sistema de venta/
├── dist/
│   └── SistemaVentas.exe
├── database/
│   └── (vacío, se creará al instalar)
├── reports/
│   └── (vacío, para facturas)
└── installer_script.iss
```

### 4.3 Compilar el Instalador

**Opción 1: Interfaz Gráfica**
1. Abrir Inno Setup
2. File > Open > Seleccionar `installer_script.iss`
3. Build > Compile
4. Esperar a que termine (1-2 minutos)
5. El instalador estará en `installer/SistemaVentas_Setup.exe`

**Opción 2: Línea de Comandos**
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

### 4.4 Probar el Instalador
1. Ir a la carpeta `installer/`
2. Ejecutar `SistemaVentas_Setup.exe`
3. Seguir el asistente de instalación
4. Verificar que se instala correctamente en `C:\Program Files\Sistema de Ventas`
5. Probar el acceso directo del escritorio

---

## PASO 5: DISTRIBUCIÓN

### El instalador incluye:
✅ El ejecutable del sistema
✅ Carpeta para base de datos
✅ Carpeta para reportes
✅ Permisos necesarios
✅ Accesos directos
✅ Desinstalador

### Compartir el Instalador:
1. Copiar `installer/SistemaVentas_Setup.exe`
2. Compartir este único archivo
3. El usuario solo necesita ejecutarlo
4. NO necesita Python ni dependencias

---

## SOLUCIÓN DE PROBLEMAS

### Error: "Python no encontrado"
```bash
# Agregar Python al PATH del sistema
# O usar ruta completa:
C:\Python312\python.exe main.py
```

### Error: "No module named 'tkinter'"
```bash
# Reinstalar Python marcando la opción "tcl/tk and IDLE"
```

### PyInstaller no genera el .exe
```bash
# Limpiar caché y volver a intentar
rmdir /s /q build dist
rmdir /s /q __pycache__
pyinstaller --clean main.py
```

### El .exe no inicia
```bash
# Generar con consola para ver errores
pyinstaller --onefile --console --name "SistemaVentas" main.py
# Ejecutar y ver mensajes de error
```

### Error al generar PDF en el .exe
```bash
# Reinstalar reportlab
pip uninstall reportlab
pip install reportlab==4.0.7

# Regenerar el .exe
pyinstaller --clean sistema_ventas.spec
```

### El instalador no se compila
- Verificar que todas las rutas en `installer_script.iss` sean correctas
- Verificar que exista `dist/SistemaVentas.exe`
- Usar rutas relativas en el script .iss

---

## PERSONALIZACIÓN DEL INSTALADOR

### Cambiar Icono del .exe
1. Tener un archivo .ico (32x32 o 64x64)
2. Modificar en el comando PyInstaller:
```bash
pyinstaller --onefile --windowed --icon=icono.ico main.py
```

### Cambiar Nombre de la Empresa
Editar `installer_script.iss`:
```iss
#define MyAppPublisher "TU NOMBRE DE EMPRESA"
```

### Cambiar Ubicación de Instalación
Editar `installer_script.iss`:
```iss
DefaultDirName={autopf}\NombreCarpeta
```

---

## VERSIONES Y ACTUALIZACIONES

### Para crear una nueva versión:
1. Actualizar código fuente
2. Cambiar versión en `installer_script.iss`:
   ```iss
   #define MyAppVersion "1.1"
   ```
3. Regenerar .exe
4. Regenerar instalador
5. Renombrar: `SistemaVentas_Setup_v1.1.exe`

---

## CHECKLIST DE DISTRIBUCIÓN

Antes de entregar el instalador:

- [ ] Probado el .exe en modo standalone
- [ ] Verificado que crea la base de datos
- [ ] Probado login con credenciales por defecto
- [ ] Verificado que genera facturas PDF
- [ ] Probado el instalador completo
- [ ] Verificado desinstalación
- [ ] Probado en Windows 10/11
- [ ] Incluida documentación (README, MANUAL_USO)
- [ ] Verificada versión en "Acerca de"

---

## ARCHIVOS FINALES PARA ENTREGAR

### Archivos Principales:
1. **SistemaVentas_Setup.exe** - Instalador completo
2. **README.md** - Documentación básica
3. **MANUAL_USO.md** - Manual de usuario completo

### Opcional (para soporte):
4. **SistemaVentas.exe** - Ejecutable standalone
5. **Código fuente** - Para desarrollo/soporte

---

## COMANDOS RÁPIDOS DE REFERENCIA

```bash
# Instalar dependencias
pip install -r requirements.txt

# Inicializar datos de ejemplo
python inicializar_datos.py

# Ejecutar en desarrollo
python main.py

# Generar .exe (automático)
build_exe.bat

# Generar .exe (manual)
pyinstaller --clean --onefile --windowed --name "SistemaVentas" main.py

# Compilar instalador
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

---

## CONTACTO Y SOPORTE

Para asistencia en el proceso de compilación:
- Revisar logs de PyInstaller en `build/`
- Revisar logs de Inno Setup en `installer/`
- Consultar documentación oficial

---

**¡Listo!** Siguiendo estos pasos tendrás un instalador profesional de tu Sistema de Ventas.

**Versión de esta guía:** 1.0  
**Fecha:** Enero 2026

# Archivo de Inicio Rápido del Sistema de Licencias

## 🚀 Pasos Rápidos para Activar Sistema de Licencias

### Paso 1: Instalar Firebase Admin SDK
```bash
pip install firebase-admin
```

### Paso 2: Obtener tu HWID
Ejecuta el script para obtener el identificador único de tu computadora:
```bash
python utils/obtener_hwid.py
```
**Resultado**: Se mostrará tu HWID (algo como: `A1B2C3D4E5F6G7H8...`)

### Paso 3: Crear Proyecto en Firebase
1. Ir a [Firebase Console](https://console.firebase.google.com/)
2. Crear nuevo proyecto o seleccionar uno existente
3. Habilitar **Cloud Firestore** (Database)
4. En **Configuración del Proyecto > Cuentas de servicio**:
   - Click en **Generar nueva clave privada**
   - Descargar archivo JSON
   - Renombrar a `serviceAccountKey.json`
   - Colocar en la **raíz del proyecto**

### Paso 4: Crear Colección de Licencias en Firestore
1. En Firestore Database, crear colección: **`licencias`**
2. Click en **Agregar documento**
3. **ID del documento**: Pegar el HWID que obtuviste (Paso 2)
4. **Agregar campos**:
   - `esta_activo`: `true` (booleano)
   - `fecha_vencimiento`: `31/12/2026` (Timestamp)
   - `cliente`: Nombre de tu cliente (string)

### Paso 5: Integrar en main.py
Agregar al **inicio** de tu archivo `main.py`:

```python
from utils.validador import validar_licencia_inicio
import sys

# Validar licencia antes de que se cargue la interfaz
resultado_licencia = validar_licencia_inicio()

if resultado_licencia is None:
    sys.exit(1)  # La licencia no es válida, salir

# Continuar con tu código normal...
print("✓ Aplicación iniciada correctamente")
```

### Paso 6: Probar la Validación
```bash
python main.py
```
- Si la licencia es válida: la aplicación se inicia normalmente
- Si la licencia NO es válida: aparece ventana de bloqueo con el HWID

---

## 📁 Archivos Creados

| Archivo | Descripción |
|---------|-----------|
| `utils/validador.py` | Módulo principal de validación |
| `utils/obtener_hwid.py` | Utilidad para obtener HWID |
| `serviceAccountKey.json.example` | Plantilla de credenciales (renombrar a `serviceAccountKey.json`) |
| `GUIA_LICENCIAS.md` | Documentación completa |
| `.env.example` | Variables de entorno (opcional) |

---

## 🔑 Gestión de Licencias en Firebase

### Registrar Nueva Licencia
En Firestore Database > `licencias`:
```json
{
  "esta_activo": true,
  "fecha_vencimiento": Timestamp(2026, 12, 31, 23, 59, 59),
  "cliente": "Juan Pérez - Tienda XYZ",
  "email": "juan@tienda.com",
  "tipo_licencia": "premium"
}
```

### Desactivar Licencia
Cambiar: `esta_activo` → `false`

### Extender Vencimiento
Modificar: `fecha_vencimiento` a fecha futura

### Licencia Permanente
Eliminar el campo `fecha_vencimiento` o dejarlo vacío

---

## ⚙️ Configuración Avanzada

### Usar Variables de Entorno (Opcional)
1. Copiar `.env.example` → `.env`
2. Modificar variables según necesario
3. El validador las cargará automáticamente

### Ruta Personalizada para Credenciales
```python
# En lugar del método por defecto
validador = ValidadorLicencias(
    credentials_path='/ruta/personalizada/serviceAccountKey.json'
)
```

---

## 🧪 Testear sin Firebase

Para desarrollo local, puedes comentar temporalmente la validación:

```python
# resultado_licencia = validar_licencia_inicio()
resultado_licencia = {'valido': True, 'mensaje': 'Test'}

# ... continuar ...
```

**⚠️ IMPORTANTE**: Descomenta antes de distribuir la aplicación

---

## 🛡️ Seguridad

✅ **Obligatorio hacer**:
- Nunca subir `serviceAccountKey.json` a Git
- Mantener `.env` privado
- Usar permisos restrictivos en Firestore
- Renovar credenciales periódicamente

❌ **NO HACER**:
- Compartir `serviceAccountKey.json`
- Hardcodear credenciales
- Subir credenciales a repositorios públicos

---

## 🆘 Solución de Problemas

### Error: "No se encontró el archivo de credenciales"
- Verifica que `serviceAccountKey.json` esté en la **raíz del proyecto**
- Verifica el **nombre exacto** del archivo

### Error: "No se puede conectar a Firebase"
- Verifica credenciales de `serviceAccountKey.json`
- Verifica que Firestore está habilitado en Firebase Console
- Verifica conexión a internet

### El HWID cambia constantemente
- Ocurre en máquinas virtuales o con configuraciones especiales
- Intenta usando uuid.getnode() como fallback (ya implementado)

---

## 📚 Más Información

- [Documentación Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Documentación Firestore](https://firebase.google.com/docs/firestore)
- [Guía Completa](GUIA_LICENCIAS.md)

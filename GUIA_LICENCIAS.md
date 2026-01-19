# Guía de Configuración del Sistema de Licencias Firebase

## 📋 Configuración Inicial

### 1. Crear Proyecto en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita **Cloud Firestore** en tu proyecto

### 2. Obtener Credenciales de Servicio

1. En Firebase Console, ve a **Configuración del Proyecto** (⚙️)
2. Ve a la pestaña **Cuentas de servicio**
3. Click en **Generar nueva clave privada**
4. Se descargará un archivo JSON
5. Renombra el archivo a `serviceAccountKey.json`
6. Coloca el archivo en la raíz del proyecto

⚠️ **IMPORTANTE**: Este archivo contiene credenciales sensibles. Nunca lo subas a Git.

### 3. Configurar Firestore

En la consola de Firebase, crea una colección llamada `licencias` con la siguiente estructura:

#### Estructura del Documento

**ID del Documento**: El HWID de la PC del cliente (ejemplo: `A1B2C3D4E5F6G7H8`)

**Campos del documento**:

```
{
  "esta_activo": true,                    // boolean
  "fecha_vencimiento": "2026-12-31",      // timestamp o string ISO
  "cliente": "Nombre del Cliente",        // string
  "email": "cliente@email.com",           // string (opcional)
  "fecha_activacion": "2026-01-19",       // timestamp (opcional)
  "tipo_licencia": "premium",             // string (opcional)
  "notas": "Licencia anual"               // string (opcional)
}
```

#### Ejemplo de Documento en Firestore:

**Documento ID**: `F9E8D7C6B5A4321ABCDEF012345`

```json
{
  "esta_activo": true,
  "fecha_vencimiento": Timestamp(2026, 12, 31, 23, 59, 59),
  "cliente": "Juan Pérez - Tienda XYZ",
  "email": "juan@tiendaxyz.com",
  "fecha_activacion": Timestamp(2026, 1, 19, 10, 0, 0),
  "tipo_licencia": "premium",
  "notas": "Licencia anual - Renovación automática"
}
```

### 4. Reglas de Seguridad de Firestore

Ve a **Firestore Database > Reglas** y configura:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir solo lectura a la colección de licencias
    match /licencias/{licenciaId} {
      allow read: if true;
      allow write: if false;  // Solo desde Firebase Console o Admin SDK
    }
  }
}
```

## 🔧 Integración en tu Aplicación

### Agregar al inicio de main.py

```python
# Al inicio del archivo main.py, antes de cualquier otra inicialización

from utils.validador import validar_licencia_inicio

# Validar licencia antes de continuar
resultado_licencia = validar_licencia_inicio()

if resultado_licencia is None:
    # La aplicación se cerrará automáticamente si la licencia no es válida
    sys.exit(1)

# Si llegamos aquí, la licencia es válida
# Continuar con la inicialización normal de la aplicación
```

### Instalación de Dependencias

```bash
pip install firebase-admin
```

O actualiza `requirements.txt` y ejecuta:
```bash
pip install -r requirements.txt
```

## 📝 Uso

### Obtener HWID de un Cliente

1. Ejecuta el módulo directamente para obtener el HWID:
   ```bash
   python utils/validador.py
   ```

2. O cuando el cliente intente abrir la app por primera vez, aparecerá una ventana mostrando su HWID

### Registrar una Nueva Licencia

1. Ve a Firebase Console > Firestore Database
2. En la colección `licencias`, click en **Agregar documento**
3. **ID del documento**: Pega el HWID que te dio el cliente
4. Agrega los campos:
   - `esta_activo`: `true`
   - `fecha_vencimiento`: Selecciona fecha (Timestamp)
   - `cliente`: Nombre del cliente
   - Otros campos opcionales

### Gestión de Licencias

#### Desactivar una licencia:
- Cambia `esta_activo` a `false`

#### Extender vencimiento:
- Modifica el campo `fecha_vencimiento`

#### Licencia permanente:
- Elimina el campo `fecha_vencimiento` o déjalo vacío

## 🔒 Seguridad

### Variables de Entorno (Alternativa)

Si prefieres no usar un archivo JSON, puedes usar variables de entorno:

1. Configura la variable `FIREBASE_CREDENTIALS_PATH`:
   ```bash
   set FIREBASE_CREDENTIALS_PATH=C:\ruta\segura\firebase_credentials.json
   ```

2. El módulo buscará automáticamente en esa ubicación

### Protección de Credenciales

✅ **Sí hacer**:
- Agregar `firebase_credentials.json` al `.gitignore`
- Mantener las credenciales fuera del control de versiones
- Usar permisos restrictivos en el archivo

❌ **No hacer**:
- Subir credenciales a Git/GitHub
- Compartir el archivo de credenciales
- Hardcodear credenciales en el código

## 🧪 Testing

### Probar el Sistema

```python
python utils/validador.py
```

Esto mostrará:
- El HWID de tu PC
- Estado de la validación
- Mensaje de error/éxito

### Casos de Prueba

1. **PC no registrada**: No crear documento con tu HWID
2. **Licencia desactivada**: Crear documento con `esta_activo: false`
3. **Licencia vencida**: Crear documento con `fecha_vencimiento` en el pasado
4. **Licencia válida**: Crear documento con todos los datos correctos

## 📊 Monitoreo

En Firebase Console puedes:
- Ver todas las licencias activas
- Consultar logs de acceso
- Exportar datos de clientes
- Configurar alertas

## ❓ Solución de Problemas

### Error: "firebase-admin no está instalado"
```bash
pip install firebase-admin
```

### Error: "No se encontró el archivo de credenciales"
- Verifica que `serviceAccountKey.json` esté en la raíz del proyecto
- Verifica el nombre del archivo (exacto, sin espacios)

### Error: "Permission denied"
- Revisa las reglas de Firestore
- Verifica que las credenciales sean correctas

### El HWID cambia constantemente
- Puede ocurrir en máquinas virtuales o con hardware específico
- Considera usar un método alternativo de identificación

## 📞 Soporte

Para más información:
- [Documentación de Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Documentación de Firestore](https://firebase.google.com/docs/firestore)

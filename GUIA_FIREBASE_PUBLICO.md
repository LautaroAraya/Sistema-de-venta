# Configuración de Firebase SIN Credenciales Sensibles

## 🔒 Sistema Seguro - Solo Lectura Pública

Este método NO requiere incluir credenciales secretas en el .exe. En su lugar:
- Usa configuración pública de Firebase (API Key, Project ID)
- Las reglas de Firestore controlan el acceso
- Los clientes solo pueden LEER su propia licencia
- Solo TÚ puedes escribir/modificar desde Firebase Console

---

## Paso 1: Obtener Configuración Pública de Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto
3. Click en ⚙️ **Configuración del proyecto**
4. Scroll hasta **Tus apps** → selecciona **Web**
5. Copia los valores del SDK config

**Verás algo así:**
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX",
  authDomain: "tu-proyecto.firebaseapp.com",
  projectId: "tu-proyecto-12345",
  storageBucket: "tu-proyecto.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456"
};
```

---

## Paso 2: Configurar firebase_config.py

Abre el archivo `firebase_config.py` y reemplaza con tus valores:

```python
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX",  # Tu API Key
    "authDomain": "tu-proyecto.firebaseapp.com",
    "projectId": "tu-proyecto-12345",  # ← IMPORTANTE
    "storageBucket": "tu-proyecto.appspot.com",
    "messagingSenderId": "123456789012",
    "appId": "1:123456789012:web:abc123def456"
}
```

---

## Paso 3: Configurar Reglas de Seguridad en Firestore

**MUY IMPORTANTE**: Estas reglas permiten que cualquiera LEA licencias, pero solo tú puedes escribir.

1. En Firebase Console → **Firestore Database**
2. Click en **Reglas**
3. Reemplaza con:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Colección de licencias
    match /licencias/{licenciaId} {
      // Permitir SOLO LECTURA a todos
      allow read: if true;
      
      // Permitir escritura SOLO desde Firebase Console o Admin SDK
      // (nadie desde las apps puede modificar)
      allow write: if false;
    }
  }
}
```

4. Click **Publicar**

---

## Paso 4: Instalar Dependencias

```bash
pip install google-cloud-firestore
```

O actualiza requirements.txt y ejecuta:
```bash
pip install -r requirements.txt
```

---

## Paso 5: Probar la Configuración

```bash
python utils/validador_public.py
```

Debería:
- Conectarse a Firestore
- Obtener tu HWID
- Validar contra la licencia

---

## Paso 6: Actualizar main.py

Cambia la importación en main.py:

**ANTES:**
```python
from utils.validador import validar_licencia_inicio
```

**DESPUÉS:**
```python
from utils.validador_public import validar_licencia_inicio
```

---

## Paso 7: Generar .exe SIN Credenciales

Actualiza `SistemaVentas.spec`:

```python
datas=[('firebase_config.py', '.')],  # Solo incluir config pública
hiddenimports=['google.cloud.firestore'],
```

Luego genera:
```bash
pyinstaller SistemaVentas.spec
```

---

## ✅ Ventajas de Este Método

✅ **Sin credenciales sensibles** en el .exe
✅ **API Key pública** puede estar en el código (no es secreto)
✅ **Reglas de Firestore** protegen los datos
✅ **Solo lectura** para las apps
✅ **Solo tú** puedes modificar licencias desde Firebase Console

---

## 🔒 Seguridad

### ¿Es seguro tener el API Key en el código?
**SÍ** - El API Key de Firebase es público y está diseñado para estar en el cliente.
La seguridad la dan las **reglas de Firestore**, no el API Key.

### ¿Qué pueden hacer los usuarios?
- ✅ Leer su propia licencia (o cualquier licencia)
- ❌ NO pueden modificar licencias
- ❌ NO pueden crear nuevas licencias
- ❌ NO pueden eliminar licencias

### ¿Qué puedes hacer tú?
- ✅ Crear licencias desde Firebase Console
- ✅ Modificar licencias
- ✅ Eliminar licencias
- ✅ Ver todas las licencias

---

## 🧪 Testing

### Probar lectura (debería funcionar):
```bash
python utils/validador_public.py
```

### Probar escritura (debería fallar):
Intenta modificar un documento desde el código - debería dar error "Permission denied"

---

## 📊 Monitoreo

En Firebase Console puedes:
- Ver todas las licencias activas
- Modificar estados y vencimientos
- Ver logs de acceso
- Exportar datos

---

## ❓ Solución de Problemas

### Error: "Permission denied"
- Verifica que las reglas de Firestore permitan lectura
- Verifica que el projectId sea correcto

### Error: "Project not found"
- Verifica el projectId en firebase_config.py
- Verifica que Firestore esté habilitado

### No se conecta
- Verifica conexión a internet
- Verifica que los datos en firebase_config.py sean correctos

---

## 📚 Más Información

- [Reglas de Seguridad Firestore](https://firebase.google.com/docs/firestore/security/rules-structure)
- [Firestore Client Libraries](https://firebase.google.com/docs/firestore/client/libraries)

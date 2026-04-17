# Deploy del Panel Tecnico Remoto

## 1) Que se implemento
- API remota segura para tecnicos: [api_tecnico_remoto.py](api_tecnico_remoto.py)
- Frontend del panel: [panel_tecnico/index.html](panel_tecnico/index.html), [panel_tecnico/app.js](panel_tecnico/app.js), [panel_tecnico/styles.css](panel_tecnico/styles.css)
- Variables de entorno ejemplo: [.env.tecnico.example](.env.tecnico.example)

## 2) Que subir a la nube
Subi estos elementos al repositorio o servicio cloud:
- [api_tecnico_remoto.py](api_tecnico_remoto.py)
- Carpeta [panel_tecnico](panel_tecnico)
- [requirements.txt](requirements.txt)

Importante:
- Para Render gratis, usar Firestore es la mejor opcion.
- SQLite solo se recomienda para pruebas locales.

## 3) Variables de entorno en la nube
Configura estas variables en Render/Railway/VPS:
- `TECNICO_USER`
- `TECNICO_PASS_HASH` (recomendado)
- `TECNICO_APP_SECRET`
- `TECNICO_TOKEN_MAX_AGE_SECONDS`
- `TECNICO_ALLOW_CORS`
- `TECNICO_EXPOSE_UNLOCK_FIELDS`
- `TECNICO_DATA_BACKEND` (usar `firestore`)
- `TECNICO_FIRESTORE_COLLECTION`
- `FIREBASE_SERVICE_ACCOUNT_JSON` (JSON completo de service account)
- `SQLITE_PATH` (solo si usas sqlite)

Si no usas `TECNICO_PASS_HASH`, podrias usar `TECNICO_PASS`, pero es menos seguro.

## 4) Comando de inicio en la nube
Usa este start command:

```bash
gunicorn api_tecnico_remoto:app --bind 0.0.0.0:$PORT
```

Si estas en un entorno Windows sin gunicorn:

```bash
python api_tecnico_remoto.py
```

Tambien puedes usar archivos listos del repo:
- [Procfile](Procfile)
- [render.yaml](render.yaml)
- [railway.json](railway.json)

## 5) URLs del sistema
- Panel tecnico: `https://tu-dominio.com/`
- Health: `https://tu-dominio.com/health`
- Login API: `POST https://tu-dominio.com/api/auth/login`

## 6) Seguridad minima recomendada
- HTTPS obligatorio.
- Cambiar `TECNICO_APP_SECRET` por uno largo y aleatorio.
- Usar `TECNICO_PASS_HASH` en lugar de password plana.
- Si el tecnico necesita desbloqueo, dejar `TECNICO_EXPOSE_UNLOCK_FIELDS=1`.
- Si no lo necesita, usar `TECNICO_EXPOSE_UNLOCK_FIELDS=0` para ocultar `contrasena` y `patron`.
- Restringir CORS a tu dominio cuando tengas frontend en dominio aparte.

## 7) Flujo sugerido para tu operacion
1. PC del local mantiene datos en SQLite.
2. Sync envia datos de reparaciones a nube (tu sistema actual ya tiene base para esto).
3. El tecnico entra al panel y trabaja sobre la base remota.
4. Si queres bidireccionalidad total, agregar un proceso que consuma cambios remotos y actualice local.

## 8) Deploy paso a paso en Render
1. Subir el proyecto a GitHub (incluyendo [api_tecnico_remoto.py](api_tecnico_remoto.py) y [panel_tecnico](panel_tecnico)).
2. En Render: New + Web Service + conectar repositorio.
3. Render detecta [render.yaml](render.yaml) automaticamente (Blueprint) o configurar manual:
	- Build Command: `pip install -r requirements.txt`
	- Start Command: `gunicorn api_tecnico_remoto:app --bind 0.0.0.0:$PORT`
4. Configurar variables de entorno:
	- `TECNICO_USER`
	- `TECNICO_PASS_HASH`
	- `TECNICO_APP_SECRET`
	- `TECNICO_TOKEN_MAX_AGE_SECONDS`
	- `TECNICO_DATA_BACKEND=firestore`
	- `TECNICO_FIRESTORE_COLLECTION=reparaciones_publicas`
	- `FIREBASE_SERVICE_ACCOUNT_JSON` (pegar JSON completo en una sola linea)
5. Deploy y probar:
	- `/health`
	- `/` (panel)

6. En la PC del local, activar sync a Firestore para que el panel tenga datos actualizados.
   Si queres incluir contrasena/patron en Firestore para el tecnico:
	- `REPARACIONES_PUBLICAS_INCLUDE_UNLOCK_FIELDS=1`

## 9) Deploy paso a paso en Railway
1. New Project + Deploy from GitHub Repo.
2. Railway usa [railway.json](railway.json) y Nixpacks.
3. Configurar variables en la pestana Variables:
	- `TECNICO_USER`
	- `TECNICO_PASS_HASH`
	- `TECNICO_APP_SECRET`
	- `TECNICO_TOKEN_MAX_AGE_SECONDS`
	- `SQLITE_PATH`
4. Redeploy y probar `/health` y panel.

## 10) Como generar TECNICO_PASS_HASH
Usa:

```bash
python tecnico_generar_hash.py
```

Luego copiar el valor generado en la variable `TECNICO_PASS_HASH` del proveedor cloud.

# Guía: Panel técnico remoto (acceso desde casa)

## Objetivo
Permitir que el técnico vea y gestione reparaciones desde otra computadora (por ejemplo, desde su casa) **sin exponer directamente** la base de datos SQLite de la PC del local.

## Recomendación principal (segura y escalable)
Usar arquitectura de sincronización a nube + panel web separado.

### Flujo recomendado
1. Sistema del local (tu app actual) guarda todo en SQLite local.
2. Un proceso de sincronización envía reparaciones a un backend en la nube.
3. El técnico entra a un panel web con usuario/clave.
4. El panel consulta la nube, no la PC del local.

---

## Lo que ya tenés en este proyecto
- API de reparaciones locales: [api.py](api.py)
- API para estado/sync: [api_estado_reparaciones.py](api_estado_reparaciones.py)
- Servicio de sync central: [sync_service.py](sync_service.py)
- Sync a Firestore: [utils/reparaciones_sync.py](utils/reparaciones_sync.py)
- Config Firebase pública: [firebase_config.py](firebase_config.py)

Esto significa que ya tenés gran parte del camino hecho.

---

## Por qué NO conviene abrir SQLite del local por Internet
- SQLite es archivo local, no motor cliente-servidor para acceso remoto concurrente.
- Exponer puertos del local (port-forwarding) aumenta mucho el riesgo de seguridad.
- Si se corta Internet o se apaga la PC del local, el técnico se queda sin acceso.

---

## Diseño del sistema aparte para técnico

### 1) Backend remoto (opción recomendada)
- Puede ser Flask/FastAPI desplegado en Render, Railway, VPS o similar.
- Guarda reparaciones en Firestore (si querés seguir con Firebase) o en PostgreSQL.
- Expone endpoints para:
  - login/autorización
  - listado de reparaciones
  - búsqueda por número de orden/DNI
  - actualización de estado
  - historial de cambios

### 2) Panel técnico web (separado)
- Frontend independiente (HTML+JS, React o similar).
- Solo accesible con login.
- Vistas mínimas:
  - Lista de reparaciones
  - Detalle de reparación
  - Cambio de estado
  - Filtros por estado/fecha

### 3) Sincronización desde el local
- Reusar [sync_service.py](sync_service.py) para enviar cambios pendientes.
- Ejecutar sync periódico (cada 1-5 min).
- Guardar `sync_pending`, `sync_attempts`, `last_sync_error` (ya está contemplado en tu código).

### 4) Seguridad mínima obligatoria
- HTTPS obligatorio en backend/panel.
- API key o JWT para llamadas de sync.
- Usuarios técnicos con roles (admin/tecnico).
- Nunca enviar campos sensibles si no son necesarios.
- Rotación de claves y logs de auditoría.

---

## Plan de implementación sugerido (rápido)

### Fase 1 (1-2 días) - MVP lectura remota
1. Dejar corriendo sync desde local a nube.
2. Crear panel técnico solo lectura.
3. Login simple (Firebase Auth o JWT).

### Fase 2 (2-4 días) - Operación completa
1. Permitir actualizar estado desde panel técnico.
2. Registrar usuario, fecha y cambio de estado (auditoría).
3. Agregar filtros, búsqueda y paginación.

### Fase 3 - Robustez
1. Reintentos automáticos de sync y alertas de fallos.
2. Notificaciones (WhatsApp/Email) al cambiar estado.
3. Backups y monitoreo.

---

## Opción alternativa (si querés acceso directo a la PC del local)
Solo para casos puntuales, no recomendado como solución final:
- VPN tipo Tailscale/ZeroTier entre ambas PCs.
- Exponer una API local con autenticación fuerte.
- Evitar compartir el archivo SQLite por red.

Aun con VPN, la opción nube + panel separado sigue siendo más estable y mantenible.

---

## Siguiente paso recomendado en este repositorio
1. Crear `panel_tecnico/` como app web separada.
2. Conectar el panel a `api_estado_reparaciones.py` o al backend central.
3. Definir qué campos verá el técnico y qué campos quedarán privados.
4. Activar autenticación antes de publicar.

Si necesitás, en el próximo paso te puedo armar el esqueleto completo de `panel_tecnico/` (login, listado, detalle y cambio de estado) integrado con tu arquitectura actual.

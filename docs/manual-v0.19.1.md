# Plataforma Educativa — Manual Técnico y de Usuario · V-0.19.1

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-17 · Licencia: MIT.

---

## Novedades de V-0.19.1 — Endurecimiento de seguridad (backend no-root)

El contenedor del backend **ya no ejecuta la aplicación como `root`**. Es una mejora de
**defensa en profundidad** (principio de menor privilegio): si algún día apareciera una RCE en
una dependencia o en el framework, el proceso comprometido no sería root dentro del contenedor,
lo que dificulta escalar privilegios y escapar del contenedor.

Cómo está montado (patrón de la imagen oficial de PostgreSQL):

- `backend/Dockerfile` instala `gosu` y crea el usuario sin privilegios `appuser` (UID/GID
  `10001` por defecto, configurables con los build-args `APP_UID`/`APP_GID` para alinear con el
  propietario de los *bind mounts* del host si se desea).
- **No** se fija `USER appuser` en la imagen. El `entrypoint.sh` arranca como `root` **solo**
  para ajustar el propietario de los volúmenes montados donde el backend escribe — la base de
  datos SQLite y los backups (`/app/data`) y la media (`/app/media`) — mediante `chown -R`, y
  acto seguido **se reinvoca con `gosu appuser`**. A partir de ahí, las migraciones Alembic, el
  seed del administrador y `uvicorn` corren ya sin privilegios.

Cambio **solo de infraestructura**: no se ha tocado código de aplicación, ni la API, ni el
esquema de base de datos. No hay migración nueva.

---

## Parte I — Manual técnico

### 1. Ficheros afectados

| Fichero | Cambio |
|---|---|
| `backend/Dockerfile` | Instala `gosu`; crea `appuser` (ARG `APP_UID`/`APP_GID`); `chown` de `data`/`media` en build. |
| `backend/entrypoint.sh` | Arranca como root, hace `chown` de los bind mounts y baja privilegios con `gosu appuser`. |
| `docs/seguridad-imagenes.md` | Documenta el setup no-root y los pasos de validación en el servidor. |

### 2. Despliegue

```
cd plataforma-educativa
docker compose up -d --build
# El entrypoint corre alembic upgrade head ya como appuser. Esta versión NO añade migraciones.
```

Para alinear con un UID/GID concreto del host:

```
docker compose build --build-arg APP_UID=<uid> --build-arg APP_GID=<gid> api
```

### 3. Validación en el servidor (recomendado)

```
# 1) uvicorn corre como appuser (no root):
docker compose exec api ps -o user,pid,comm
#    -> la línea de python/uvicorn debe mostrar 'appuser'

# 2) Sin errores de permisos; migraciones y seed correctos:
docker compose logs api | grep -i -E "permission|denied|alembic|admin"
```

Si los bind mounts tenían ficheros de propietario `root` de versiones anteriores, el `chown` del
entrypoint los reasigna a `appuser` en el primer arranque (coste único; puede tardar algo si
`./media` tiene muchos ficheros).

### 4. Notas de seguridad

- El `healthcheck` del compose se ejecuta vía `docker exec` (como root); solo hace un `urlopen`
  a `localhost:8000/health`, no requiere privilegios y sigue funcionando.
- El aislamiento del sandbox de ejercicios, la sanitización asimétrica del HTML de artículos y el
  tratamiento de datos de menores no cambian.

### 5. Tests

Cambio solo de infraestructura; la suite de aplicación sigue en verde.

```
cd backend && python -m pytest tests/unit tests/integration -q   # 205
cd frontend && npm run test:e2e                                  # 9 E2E
```

---

## Parte II — Manual de usuario

No hay cambios visibles para administradores, editores ni visitantes en esta versión: es una
mejora interna de seguridad del despliegue.

### Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.19.1) | Backend sin privilegios (usuario no-root con gosu) en Docker. |
| Hecho (V-0.19.0) | Iconos de red en artículos + autor de cada versión. |
| Pendiente (UI) | Pie de la web siempre visible; acciones de admin/editor siempre visibles. |

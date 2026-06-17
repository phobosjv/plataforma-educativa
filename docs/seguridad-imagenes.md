# Seguridad de las imágenes Docker — escaneo y endurecimiento

> Guía operativa para reducir y vigilar las vulnerabilidades de las imágenes del proyecto.
> El escaneo se hace **en el servidor** (o en CI): en la máquina de desarrollo Docker no está
> en el `PATH`, así que el build y el escáner solo se validan donde corre el stack.

## 1. Qué se hace en los Dockerfiles (V-0.10.1)

- **Backend** (`backend/Dockerfile`): base `python:3.12-slim-bookworm` (release de Debian
  explícita) + `apt-get upgrade -y` en el build para aplicar los **parches de seguridad del SO**
  publicados después de la imagen base (ahí está el grueso de los hallazgos). Se actualizan
  `pip`/`setuptools`/`wheel` (sus versiones antiguas son un hallazgo recurrente del escáner).
- **Frontend** (`frontend/Dockerfile`): etapa final `nginx:alpine` con `apk upgrade --no-cache`.

> El escáner del IDE marca el **tag base** *antes* de que se ejecute el `apt-get upgrade`. Tras el
> build, las CVEs que tengan corrección en Debian quedan parcheadas; las que el escáner siga
> mostrando suelen ser **"no fix available"** (sin parche aún en Debian), comunes a toda imagen
> Debian. Para confirmarlo, escanea la imagen **ya construida** (no el tag base):

## 2. Escanear las imágenes construidas (Trivy)

```bash
# En el servidor, desde /opt/plataforma-educativa
docker compose build

# Instalar Trivy (una vez): https://aquasecurity.github.io/trivy
# Debian/Ubuntu:
#   sudo apt-get install -y wget apt-transport-https gnupg
#   wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo gpg --dearmor -o /usr/share/keyrings/trivy.gpg
#   echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | sudo tee /etc/apt/sources.list.d/trivy.list
#   sudo apt-get update && sudo apt-get install -y trivy

# Escanear el backend y el frontend ya construidos (nombres según el proyecto compose):
trivy image --severity HIGH,CRITICAL --ignore-unfixed plataforma-educativa-api
trivy image --severity HIGH,CRITICAL --ignore-unfixed plataforma-educativa-frontend
```

- `--ignore-unfixed` oculta las CVEs **sin parche disponible** (no son accionables) y deja ver
  solo las que SÍ se pueden corregir. Quita el flag para ver el total.
- `docker images` lista los nombres reales de las imágenes si difieren del prefijo del proyecto.

## 3. Fijar la base por digest (reproducibilidad total, opcional)

El tag `python:3.12-slim-bookworm` sigue moviéndose con cada parche. Para builds idénticos byte a
byte, fíjala por digest:

```bash
docker buildx imagetools inspect python:3.12-slim-bookworm   # copia el sha256 "Digest"
```

y en `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim-bookworm@sha256:<digest>
```

Inconveniente: hay que actualizar el digest a mano para recibir nuevos parches (conviene revisarlo
cada cierto tiempo o automatizarlo).

## 4. Backend sin privilegios (usuario no-root) — V-0.19.1

El contenedor del backend ya **no ejecuta la aplicación como `root`**. Aplica el principio de
**menor privilegio**: si apareciera una RCE (en una dependencia, FastAPI, etc.), el proceso
comprometido no sería root dentro del contenedor, lo que dificulta escalar y escapar.

Cómo está montado (patrón de la imagen oficial de postgres):

- `backend/Dockerfile` instala `gosu` y crea el usuario `appuser` (UID/GID `10001` por defecto,
  configurables con los build-args `APP_UID`/`APP_GID`).
- **No** se fija `USER appuser` en la imagen: el `entrypoint.sh` arranca como `root` SOLO para
  hacer `chown -R appuser:appuser /app/data /app/media` (los *bind mounts* donde se escribe la BD
  SQLite, los backups y la media) y, acto seguido, **se reinvoca con `gosu appuser`**. A partir de
  ahí las migraciones Alembic, el seed del admin y `uvicorn` corren ya sin privilegios.

### Validación en el servidor (recomendado tras desplegar)

```bash
# Reconstruir y levantar
docker compose up -d --build api

# 1) El proceso de uvicorn corre como appuser (no root):
docker compose exec api ps -o user,pid,comm
#   -> la línea de 'uvicorn'/'python' debe mostrar 'appuser', no 'root'

# 2) La BD y la media se escriben correctamente (sin errores de permisos):
docker compose logs api | grep -i -E "permission|denied|alembic|admin"
#   -> migraciones aplicadas y, en primer arranque, "Usuario admin creado"
```

Si los *bind mounts* del host tenían ficheros de propietario `root` de versiones anteriores, el
`chown` del entrypoint los reasigna a `appuser` en el primer arranque (puede tardar un poco si
`./media` tiene muchos ficheros; es un coste único). Para alinear con un UID concreto del host,
reconstruir con `docker compose build --build-arg APP_UID=<uid> --build-arg APP_GID=<gid> api`.

> Nota: el `healthcheck` del compose se ejecuta como root (vía `docker exec`); solo hace un
> `urlopen` a `localhost:8000/health`, no necesita privilegios especiales y sigue funcionando.

## 5. Hecho / histórico

- **`python-jose` → `PyJWT`** (V-0.17.1): migrada la gestión de JWT a la librería de referencia
  (mejor mantenida, sin el histórico de CVEs de `python-jose`). Aislado en `auth_service.py`.
```

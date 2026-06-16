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

## 4. Endurecimiento pendiente (futuro, requiere validar en el servidor)

- **Ejecutar como usuario no-root**: el contenedor del backend corre como `root`. Pasar a un usuario
  sin privilegios es un endurecimiento valioso, pero el backend escribe en los *bind mounts*
  `./data` (BD SQLite + backups) y `./media`; un usuario no-root necesita que esos directorios del
  host le pertenezcan (UID coincidente) o usar `gosu`/`su-exec` para bajar privilegios en el
  entrypoint tras hacer `chown`. **No se aplicó aún** para no arriesgar la escritura de la BD en
  producción sin poder probarlo (Docker no está disponible en la máquina de desarrollo).
- **Revisar `python-jose`**: histórico de CVEs; valorar migrar a `pyjwt` en el futuro (cambia
  `auth_service.py`).
```

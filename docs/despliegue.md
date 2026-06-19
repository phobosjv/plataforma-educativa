# Despliegue en producción (Docker + Caddy + HTTPS)

Guía para poner en marcha la plataforma en un **servidor recién instalado** y para
**actualizarlo** después sin perder contenido. El stack expone a internet **solo Caddy**
(80/443), que termina el HTTPS (Let's Encrypt) y reparte a los servicios internos
(`frontend`, `api`, `sandbox`).

> Carpeta de despliegue de referencia: `/opt/portal-educacion`. Ajusta las rutas si usas otra.

---

## 1. Requisitos previos (una sola vez en el servidor)

- **Docker Engine + plugin Compose v2** instalados:
  ```bash
  curl -fsSL https://get.docker.com | sh
  docker compose version    # debe responder (v2)
  ```
- **DNS**: registros **A** de `APP_DOMAIN` y `SANDBOX_DOMAIN` (y, si los usas,
  `WEBMIN_DOMAIN` / `PORTAINER_DOMAIN`) apuntando a la IP pública del servidor.
- **Router/firewall**: puertos **80 y 443** (TCP, y 443/UDP para HTTP/3) redirigidos al servidor.

---

## 2. Primera instalación (servidor recién instalado)

```bash
# 1) Colocar el código en /opt/portal-educacion
sudo mkdir -p /opt/portal-educacion && cd /opt/portal-educacion
# (sube y descomprime el zip de distribución aquí, o clona el repo)
unzip -oq plataforma-educativa-vX.Y.Z.zip
cp -rf plataforma-educativa-vX.Y.Z/. .

# 2) Crear y EDITAR el .env (dominios, email ACME, SECRET_KEY, admin inicial)
cp .env.example .env
nano .env
#   APP_DOMAIN, SANDBOX_DOMAIN  -> tus dominios reales (NO localhost)
#   ACME_EMAIL                  -> tu email (avisos de Let's Encrypt)
#   SECRET_KEY                  -> cadena larga y aleatoria (>= 32 caracteres)
#   DEFAULT_ADMIN_EMAIL/PASSWORD-> credenciales del primer admin
#   (opcional) WEBMIN_DOMAIN / PORTAINER_DOMAIN  -> ver sección 4

# 3) Levantar el stack (build + arranque). Caddy pide los certificados al primer acceso.
docker compose up -d --build

# 4) Comprobar
docker compose ps
docker compose logs -f caddy     # ver la emisión de certificados (Ctrl+C para salir)
```

Al primer arranque, el `entrypoint` del backend aplica las migraciones (`alembic upgrade head`)
y crea el admin inicial si la BD está vacía. Entra en `https://APP_DOMAIN` y haz login.

`SECRET_KEY`, `SANDBOX_BASE_URL`, `APP_ORIGINS` y `CORS_ALLOW_ORIGINS` se derivan de los dominios
en `docker-compose.yml`: no hace falta tocarlos a mano.

---

## 3. Actualizaciones posteriores (sin perder contenido)

La BD (`./data/app.sqlite3`) y los ficheros (`./media`) son **bind mounts** del host: no van en
la imagen ni en el zip, así que una actualización no los toca. Las migraciones se aplican solas.

```bash
# Desde /opt (un nivel por encima de la carpeta del proyecto):
tar czf backup-$(date +%F-%H%M).tgz -C portal-educacion data media .env
unzip -oq plataforma-educativa-vX.Y.Z.zip
cp -rf plataforma-educativa-vX.Y.Z/. portal-educacion/
cd portal-educacion && docker compose up -d --build
```

> ⚠️ **Nunca uses `docker compose down -v`**: borra el volumen `caddy_data` con los certificados
> de Let's Encrypt (riesgo de rate limit al re-emitirlos).
>
> ⚠️ **Variables nuevas en el `.env`**: `cp -rf` **no** pisa tu `.env`. Si una versión añade
> variables al `.env.example`, añádelas a mano a tu `.env` con tus valores reales.

---

## 4. (OPCIONAL) Webmin y Portainer por HTTPS detrás de Caddy

Caddy puede servir tus paneles de administración del servidor por subdominio HTTPS (y así puedes
cerrar sus puertos a internet). Define en el `.env` solo los que uses:

> Plantilla reutilizable (sirve también para otros servidores con este mismo patrón Caddy+Docker,
> aunque la web sea otro proyecto), con prompt copy-paste incluido: **`docs/proxy-webmin-portainer.md`**.

```bash
WEBMIN_DOMAIN=webmin.tudominio.com
PORTAINER_DOMAIN=portainer.tudominio.com
```
Luego recarga Caddy: `docker compose up -d caddy`.

### 4.1 Webmin (proceso del HOST, puerto 10000)

Tras el proxy, Webmin necesita un ajuste **una sola vez en el host** para no dar el aviso de
"Trusted Referrers" ni obligar a recargar (genera redirecciones al host interno). Como root:

```bash
sudo bash -c '
# Webmin sabe que va detrás de un proxy HTTPS
grep -q "^redirect_ssl=" /etc/webmin/miniserv.conf \
  && sed -i "s/^redirect_ssl=.*/redirect_ssl=1/" /etc/webmin/miniserv.conf \
  || echo "redirect_ssl=1" >> /etc/webmin/miniserv.conf

# Referers de confianza (sustituye webmin.tudominio.com por tu dominio real)
grep -q "^referers=" /etc/webmin/config \
  && sed -i "s/^referers=.*/referers=webmin.tudominio.com host.docker.internal/" /etc/webmin/config \
  || echo "referers=webmin.tudominio.com host.docker.internal" >> /etc/webmin/config

systemctl restart webmin
'
```
(Opcional, quita el aviso de `/tmp` en tmpfs: `mkdir -p /var/webmin/tmp` y en
`/etc/webmin/config` añade `tempdir=/var/webmin/tmp`.)

### 4.2 Portainer (CONTENEDOR)

Portainer corre como contenedor **externo** a este stack. Para que el proxy funcione (y evitar su
error CSRF `Forbidden - origin invalid`), Caddy le habla por la **red interna** del stack. Conecta
Portainer a esa red **una vez** tras desplegar:

```bash
cd /opt/portal-educacion
./connect-portainer.sh
docker compose restart caddy
```

> Repite `./connect-portainer.sh` si recreas el contenedor de Portainer (`docker rm`/`run`) o si
> haces `docker compose down` (eso recrea la red del stack y se pierde la conexión).

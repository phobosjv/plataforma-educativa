# Manual técnico y de usuario — V-0.21.6

CMS educativo interactivo para infantil y primaria. Esta versión es un **cambio de despliegue**:
afina el proxy inverso de **Portainer** detrás de Caddy y documenta la **primera instalación** en
un servidor recién instalado. Sin cambios de backend, API, esquema ni código de la aplicación.

## Novedades de V-0.21.6

### Proxy inverso de Portainer (arreglo)
- El bloque `PORTAINER_DOMAIN` del `caddy/Caddyfile` deja de usar
  `https://host.docker.internal:9443` y pasa a `reverse_proxy portainer:9000`: HTTP por la **red
  interna** del stack, por **nombre de contenedor**, forzando el `Host` público con `header_up`.
- **Motivo:** alcanzando a Portainer por su puerto publicado, recibía un `Host` interno
  (`host.docker.internal:9443`); su protección **CSRF** (Portainer 2.20+) compara ese `Host` con
  el `Origin` del navegador y, al no coincidir, rechazaba las acciones de escritura con
  `Forbidden - origin invalid` (no se podían reiniciar/parar contenedores). Además el doble TLS lo
  hacía lento.
- **Webmin** no cambia: sigue por `host.docker.internal:10000` (es un proceso del host, no un
  contenedor).

### Script de post-despliegue
- **`connect-portainer.sh`** conecta el contenedor `portainer` (externo al stack) a la red de
  Caddy. Necesario una vez tras desplegar; idempotente. Portainer vive fuera del `docker-compose`,
  así que su red no se puede declarar en el compose.

### Documentación de despliegue
- **`docs/despliegue.md`**: primera instalación en servidor recién instalado, actualizaciones sin
  pérdida de contenido, y alta opcional de Webmin/Portainer por HTTPS (con los ajustes de Webmin
  en `/etc/webmin/`).

## Primera instalación (resumen)

```bash
sudo mkdir -p /opt/portal-educacion && cd /opt/portal-educacion
unzip -oq plataforma-educativa-v0.21.6.zip
cp -rf plataforma-educativa-v0.21.6/. .
cp .env.example .env          # dominios reales, ACME_EMAIL, SECRET_KEY, admin inicial
docker compose up -d --build

# (opcional) Portainer detrás del proxy, una vez:
./connect-portainer.sh && docker compose restart caddy
```

Requisitos: Docker + Compose v2, DNS A de los dominios apuntando al servidor, puertos 80/443
abiertos. Detalle completo en `docs/despliegue.md`.

## Webmin tras el proxy (ajuste único en el host)

```bash
sudo bash -c '
grep -q "^redirect_ssl=" /etc/webmin/miniserv.conf \
  && sed -i "s/^redirect_ssl=.*/redirect_ssl=1/" /etc/webmin/miniserv.conf \
  || echo "redirect_ssl=1" >> /etc/webmin/miniserv.conf
grep -q "^referers=" /etc/webmin/config \
  && sed -i "s/^referers=.*/referers=webmin.tudominio.com host.docker.internal/" /etc/webmin/config \
  || echo "referers=webmin.tudominio.com host.docker.internal" >> /etc/webmin/config
systemctl restart webmin
'
```

## Roadmap

| Estado | Versión | Cambio |
|--------|---------|--------|
| Hecho  | V-0.21.6 | Proxy de Portainer por red interna + script + guía de despliegue. |
| Hecho  | V-0.21.5 | Proxy inverso opcional Webmin/Portainer vía Caddy. |
| Hecho  | V-0.21.4 | Tabla de contenidos: columnas de taxonomía, orden y paginación. |

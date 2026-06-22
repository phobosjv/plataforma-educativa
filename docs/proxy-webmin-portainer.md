# Webmin y Portainer detrás de Caddy (plantilla reutilizable)

Guía y **prompt copy-paste** para servir Webmin y Portainer por HTTPS detrás de Caddy en cualquier
servidor con este mismo patrón (Caddy + Docker), sea este proyecto u otro distinto que comparta el
sistema de gestión. Solo cambia `<MIDOMINIO>` (y la carpeta de despliegue).

- **Webmin**: proceso del **HOST**, puerto 10000 → `host.docker.internal:10000`.
- **Portainer**: **CONTENEDOR** (publica 9443/8000, expone 9000) → por la **red interna** de Caddy.

## Por qué falla cada uno

- **Webmin** tras el proxy avisa de *Trusted Referrers* y genera redirecciones al host interno
  (obliga a recargar) porque recibe un `Host` distinto del dominio público y cree que va sin TLS.
  Además, su **terminal** (WebSocket) se queda en `CONNECTING…` y el log
  `/var/webmin/miniserv.error` muestra `Invalid Websockets origin`. Esto tiene DOS causas que hay que
  resolver juntas:
  1. **El upgrade WebSocket no llega a Webmin** sobre un upstream HTTPS si Caddy no fuerza HTTP/1.1
     (el WS aparece como `Finished`/0 B en vez de `101`). Se arregla con `versions 1.1` en el
     `transport http` del bloque de Caddy.
  2. **Webmin rechaza el origen**: su anti-CSWSH (`handle_websocket_request` en `miniserv.pl`) acepta
     el `Origin` del navegador (`https://webmin.<MIDOMINIO>`) solo si está en
     `get_websocket_allowed_origins()`. Esa lista se arma con `host:puerto` del acceso directo
     (lleva el puerto interno 10000 → no casa), las cabeceras `X-Forwarded-*` (solo si
     `trust_real_ip=1`), `websocket_host` y `websocket_extra_origins`. Ni `header_up Host` ni
     `referers` la alimentan. **Solución: `websocket_extra_origins=https://webmin.<MIDOMINIO>` en
     `/etc/webmin/miniserv.conf`** (alternativa equivalente: `trust_real_ip=1`, ya que Caddy manda
     `X-Forwarded-Host/Proto`, pero es menos quirúrgico). `header_up Host {host}` se mantiene igualmente
     para alinear referers/redirecciones de las páginas normales.
- **Portainer** da `Forbidden - origin invalid` al reiniciar/parar contenedores: su protección CSRF
  (Portainer 2.20+) compara el `Host` que recibe con el `Origin` del navegador. Alcanzándolo por el
  puerto publicado recibe un `Host` interno (`host.docker.internal:9443`) → no coincide → rechaza.
  Además el doble TLS (Caddy→9443 autofirmado) lo hace lento.

## Dos lecciones que ahorran horas

1. **`caddy reload` puede NO aplicar la config viva** (dice `Valid configuration` pero sigue sirviendo
   la anterior). Aplica siempre con **`docker compose restart caddy`** (o `docker restart <caddy>`).
2. **Caddy, en `reverse_proxy https://host:PUERTO` (upstream HTTPS), manda al upstream
   `Host: host:PUERTO` por defecto** (no el host del cliente). Por eso Portainer ve el host interno;
   hay que forzar `header_up Host {host}`.

---

## Solución

### Webmin — bloque del Caddyfile

Webmin habla HTTPS con cert autofirmado, así que se omite la verificación TLS interna. `versions 1.1`
es **imprescindible para el terminal** (el WebSocket necesita HTTP/1.1; si no, no llega a Webmin).
`header_up Host {host}` alinea referers/redirecciones de las páginas normales.

```caddyfile
webmin.<MIDOMINIO> {
    reverse_proxy https://host.docker.internal:10000 {
        transport http {
            tls_insecure_skip_verify
            versions 1.1
        }
        header_up Host {host}
        header_up X-Forwarded-Proto https
        header_up X-Forwarded-Host {host}
    }
}
```

Aplica **reiniciando Caddy** (no `reload`): `docker compose restart caddy`. Requiere
`extra_hosts: ["host.docker.internal:host-gateway"]` en el servicio Caddy del compose.

### Webmin (en el HOST, una vez — no va en el zip)

```bash
sudo bash -c '
grep -q "^redirect_ssl=" /etc/webmin/miniserv.conf \
  && sed -i "s/^redirect_ssl=.*/redirect_ssl=1/" /etc/webmin/miniserv.conf \
  || echo "redirect_ssl=1" >> /etc/webmin/miniserv.conf

grep -q "^referers=" /etc/webmin/config \
  && sed -i "s/^referers=.*/referers=webmin.<MIDOMINIO> host.docker.internal/" /etc/webmin/config \
  || echo "referers=webmin.<MIDOMINIO> host.docker.internal" >> /etc/webmin/config

# TERMINAL (WebSocket): mete el origen publico en la lista blanca de WebSockets de miniserv.
# Sin esto el terminal queda en "CONNECTING..." y el log da "Invalid Websockets origin", porque la
# lista de origenes permitidos NO se alimenta de Host ni de referers (ver get_websocket_allowed_origins
# en miniserv.pl). OJO: va en miniserv.conf, NO en config.
grep -q "^websocket_extra_origins=" /etc/webmin/miniserv.conf \
  && sed -i "s|^websocket_extra_origins=.*|websocket_extra_origins=https://webmin.<MIDOMINIO>|" /etc/webmin/miniserv.conf \
  || echo "websocket_extra_origins=https://webmin.<MIDOMINIO>" >> /etc/webmin/miniserv.conf

# (opcional, quita el aviso de /tmp en tmpfs)
mkdir -p /var/webmin/tmp
grep -q "^tempdir=" /etc/webmin/config \
  && sed -i "s|^tempdir=.*|tempdir=/var/webmin/tmp|" /etc/webmin/config \
  || echo "tempdir=/var/webmin/tmp" >> /etc/webmin/config

systemctl restart webmin
'
```

### Portainer (Caddyfile + 1 paso manual)

1. Conectar el contenedor `portainer` a la red de Caddy:
   ```bash
   CADDY=$(docker ps --format '{{.Names}}' | grep -i caddy | head -n1)
   NET=$(docker inspect "$CADDY" -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}' | head -n1)
   docker network connect "$NET" portainer
   ```
2. Bloque de Portainer en el Caddyfile (deja el dominio como esté: literal o `{$PORTAINER_DOMAIN}`):
   ```caddyfile
   portainer.<MIDOMINIO> {
       reverse_proxy portainer:9000 {
           header_up Host {host}
           header_up X-Forwarded-Host {host}
           header_up X-Forwarded-Proto https
       }
   }
   ```
3. Aplicar **reiniciando Caddy** (no `reload`): `docker compose restart caddy` (o `docker restart <caddy>`).
4. Verificar: en el navegador `Ctrl+Shift+R` en `https://portainer.<MIDOMINIO>` y reiniciar un
   contenedor. Si falla, `docker logs --tail 5 portainer` → el campo `host=` debe ser
   `portainer.<MIDOMINIO>` (no `host.docker.internal`). Si el VPS va en UTC, compara con `date` para
   no confundir logs viejos con nuevos.

> Repite el `docker network connect` si recreas Portainer (`docker rm`/`run`) o haces
> `docker compose down` (recrean la red).

---

## Prompt copy-paste (para arrancar en otro proyecto/servidor)

```
En este servidor tengo Webmin (proceso del HOST, puerto 10000) y Portainer (CONTENEDOR; publica 9443 y
8000, expone 9000) servidos por HTTPS detrás de Caddy (que va con Docker y tiene su Caddyfile) por
subdominio: webmin.<MIDOMINIO> y portainer.<MIDOMINIO>. La web principal de este servidor es OTRO
proyecto: NO la toques; solo arregla el acceso a Webmin y Portainer tras el proxy. Ve directo a la
solución ya probada, pero VERIFICA cada paso.

PASO 0 — DESCUBRE EL ENTORNO (no asumas rutas):
- Contenedor de Caddy:  docker ps --format '{{.Names}}\t{{.Image}}' | grep -i caddy
- Su Caddyfile (mounts):  docker inspect <CADDY> -f '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
- Su red:  docker inspect <CADDY> -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}'
- Existe 'portainer':  docker ps --format '{{.Names}}' | grep -x portainer
Dime lo que encuentres antes de modificar nada.

WEBMIN — bloque del Caddyfile (necesario para que el TERMINAL, que va por WebSocket, llegue a Webmin):
   reverse_proxy https://host.docker.internal:10000 {
       transport http { tls_insecure_skip_verify; versions 1.1 }
       header_up Host {host}
       header_up X-Forwarded-Proto https
       header_up X-Forwarded-Host {host}
   }
   'versions 1.1' es imprescindible: el WebSocket necesita HTTP/1.1; sobre upstream HTTPS, sin esto el
   upgrade no llega a Webmin (el WS sale "Finished"/0 B en vez de "101"). Aplica reiniciando Caddy (no
   'reload'). Requiere extra_hosts host.docker.internal:host-gateway en el servicio Caddy del compose.

WEBMIN (HOST, /etc/webmin/, una vez; idempotente con sudo bash -c):
- miniserv.conf: redirect_ssl=1
- config: referers=webmin.<MIDOMINIO> host.docker.internal
- TERMINAL (WebSocket): miniserv.conf -> websocket_extra_origins=https://webmin.<MIDOMINIO>
  (sin esto el terminal da "Invalid Websockets origin"; la lista de origenes permitidos NO usa Host ni
  referers, ver get_websocket_allowed_origins en miniserv.pl. Alternativa: trust_real_ip=1.)
- (cosmético tmpfs) mkdir -p /var/webmin/tmp ; config: tempdir=/var/webmin/tmp
- systemctl restart webmin ; verifica con grep.

PORTAINER (Caddyfile + 1 paso manual). Causa: su CSRF (2.20+) compara Host vs Origin; por el puerto
publicado recibe un Host interno y rechaza con "Forbidden - origin invalid". NO uses
host.docker.internal:9443 (falla y va lento). Solución: red interna de Caddy.
1) docker network connect <RED_DE_CADDY> portainer ; verifica con docker inspect portainer.
2) En el Caddyfile, bloque de portainer.<MIDOMINIO> (copia .bak antes):
   reverse_proxy portainer:9000 {
       header_up Host {host}
       header_up X-Forwarded-Host {host}
       header_up X-Forwarded-Proto https
   }
3) Aplica REINICIANDO Caddy (docker compose restart <caddy> o docker restart <CADDY>), NO 'caddy reload'
   (el reload puede decir "Valid configuration" y NO aplicar la config; solo el restart la activa).
4) Verifica en el navegador (Ctrl+Shift+R + reiniciar un contenedor). Si falla, docker logs --tail 5
   portainer -> campo host= debe ser portainer.<MIDOMINIO>. Si el VPS va en UTC, compara con 'date'.

Confírmame cada verificación antes de pasar de Webmin a Portainer.
```

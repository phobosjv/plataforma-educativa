# Plataforma Educativa — Manual Técnico y de Usuario · V-0.21.5

> CMS educativo interactivo para infantil y primaria. Acceso público sin cuentas de alumno.
> Roles `admin` y `editor`. Arquitectura hexagonal. Fecha: 2026-06-19 · Licencia: MIT.

---

## Novedades de V-0.21.5 — Proxy inverso opcional para paneles de administración

Caddy puede ahora servir por HTTPS (con certificado de Let's Encrypt) dos paneles de administración
del servidor que corren **fuera** de este stack, mediante subdominios configurables en el `.env`:

- `WEBMIN_DOMAIN` → **Webmin** en el host (puerto 10000).
- `PORTAINER_DOMAIN` → **Portainer** (contenedor que publica el 9443 en el host).

Así entras por `https://webmin.…` y `https://portainer.…` (sin el puerto) y puedes **cerrar a
internet los puertos 10000 y 9443**. Es un cambio **solo de despliegue**: no toca backend, API,
esquema ni el código de la aplicación.

---

## Parte I — Manual técnico

### 1. Cambios

| Área | Cambio |
|---|---|
| `caddy/Caddyfile` | Dos bloques nuevos: `{$WEBMIN_DOMAIN}` → `host.docker.internal:10000` y `{$PORTAINER_DOMAIN}` → `host.docker.internal:9443`, con `tls_insecure_skip_verify`. |
| `docker-compose.yml` | El servicio `caddy` recibe `WEBMIN_DOMAIN`/`PORTAINER_DOMAIN` (por defecto `*.localhost`) y un `extra_hosts: host.docker.internal:host-gateway`. |
| `.env.example` | Documenta las dos variables opcionales. |

### 2. Cómo funciona

- Webmin y Portainer exponen HTTPS con **certificado autofirmado** en su puerto. Caddy reenvía con
  `tls_insecure_skip_verify` (la verificación interna se omite a propósito); el cifrado de cara a
  internet lo aporta Caddy con su certificado de Let's Encrypt.
- `host.docker.internal` resuelve al host gracias al `extra_hosts: …:host-gateway`. Webmin escucha en
  el host (10000) y Portainer publica el 9443 en el host, así que ambos se alcanzan por esa ruta.
- **Opcionalidad sin romper nada**: si no defines las variables, `docker-compose` pasa
  `webmin.localhost` / `portainer.localhost`. Caddy sirve esos bloques con su **CA interna** (no pide
  certificado a Let's Encrypt) y quedan inertes, sin afectar a despliegues que no usen estos paneles.

### 3. Requisitos para activarlos

- Registro **DNS A** de cada subdominio apuntando a la IP del servidor (un CNAME al dominio principal
  también sirve).
- **Portainer** debe **publicar** el 9443 en el host (`docker ps` debe mostrar `0.0.0.0:9443->9443/tcp`).
  Si solo lo tuvieras en red interna, habría que proxyar por nombre de contenedor en una red compartida.
- **Webmin**: si aparece error de *referrer* al entrar por el subdominio, añade el dominio en
  *Webmin Configuration → Trusted Referrers*.

---

## Parte II — Manual de usuario

### 4. Activar el acceso HTTPS a Webmin/Portainer

1. En el `.env` del servidor define (los que uses):
   ```
   WEBMIN_DOMAIN=webmin.tudominio.com
   PORTAINER_DOMAIN=portainer.tudominio.com
   ```
2. Asegúrate del DNS de esos subdominios y de que Portainer publica el 9443.
3. Recarga Caddy: `docker compose up -d caddy` (o el `up -d --build` del despliegue completo).
4. Entra por `https://webmin.tudominio.com` y `https://portainer.tudominio.com`. Caddy emite el
   certificado al primer acceso. Tras comprobarlo, puedes cerrar 10000/9443 a internet en el firewall.

### 5. Roadmap

| Estado | Elemento |
|---|---|
| Hecho (V-0.21.5) | Proxy inverso opcional para Webmin/Portainer vía Caddy. |
| Hecho (V-0.21.4) | Tabla de contenidos: columnas de taxonomía, orden por columna y paginación. |
| Hecho (V-0.21.3) | Sección «Monetización y RRSS» separada de «Apariencia». |

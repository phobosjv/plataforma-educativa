# Manual técnico y de usuario — V-0.21.7

CMS educativo interactivo para infantil y primaria. Esta versión es **solo documentación**:
empaqueta la **plantilla reutilizable** para exponer Webmin y Portainer por HTTPS detrás de Caddy,
que se creó justo después de cerrar el zip de V-0.21.6 y por eso quedó fuera de él. Sin cambios de
backend, API, esquema ni código de la aplicación.

## Novedades de V-0.21.7

### Plantilla portátil de proxy Webmin/Portainer
- **`docs/proxy-webmin-portainer.md`**: guía reutilizable para poner **Webmin** y **Portainer**
  tras un proxy inverso **Caddy** con HTTPS de Let's Encrypt, en **cualquier** servidor (no solo
  este proyecto). Pensada para el segundo VPS del usuario, que tiene la misma situación (otra web,
  mismo sistema de gestión, también Caddy + Docker).
- Incluye un **prompt copy-paste portátil**: un PASO 0 que descubre el nombre del contenedor de
  Portainer, la ruta real del Caddyfile y la red de Caddy, **sin asumir** rutas de este proyecto.
- Enlazada desde `docs/despliegue.md`.

### Las dos lecciones clave (aprendidas en producción)
1. **`caddy reload` no aplica la configuración en caliente.** Incluso
   `docker compose exec caddy caddy reload` responde "Valid configuration" pero sigue sirviendo la
   configuración anterior. Solo **`docker compose restart caddy`** activa los cambios. Esto causó
   horas de confusión probando configuraciones que no estaban vivas.
2. **Con upstream HTTPS, Caddy reescribe el `Host`.** Al hacer
   `reverse_proxy https://host:puerto`, Caddy manda al upstream el `Host` del propio upstream por
   defecto, no el del cliente. Hay que forzar `header_up Host {host}` para que el destino (p. ej.
   la protección CSRF de Portainer) reciba el dominio público y la comprobación cuadre.

## Por qué este release
La plantilla `docs/proxy-webmin-portainer.md` se creó en el commit `a2dc755`, posterior al zip de
V-0.21.6. Para que quede disponible dentro de un paquete de distribución versionado, se empaqueta
ahora como V-0.21.7 (PATCH de documentación).

## Instalación y despliegue
Sin cambios respecto a V-0.21.6. Consultar `docs/despliegue.md` para la primera instalación en un
servidor recién instalado, la actualización sin pérdida de contenido y el alta opcional de
Webmin/Portainer por HTTPS.

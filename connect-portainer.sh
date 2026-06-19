#!/bin/sh
# connect-portainer.sh
# Conecta el contenedor EXTERNO 'portainer' a la red de este stack (la de Caddy). Es necesario
# para que el proxy inverso de PORTAINER_DOMAIN funcione: caddy/Caddyfile habla con Portainer por
# la red interna (reverse_proxy portainer:9000), evitando el "Forbidden - origin invalid" de su
# protección CSRF y el doble TLS.
#
# Portainer vive FUERA de este docker-compose, así que su red no se puede declarar en el compose.
# Ejecuta este script UNA vez tras el primer despliegue. Vuelve a ejecutarlo si recreas Portainer
# (docker rm/run) o si haces 'docker compose down' (eso elimina y recrea la red del stack).
#
# Uso (desde la carpeta del proyecto):  ./connect-portainer.sh
set -eu
cd "$(dirname "$0")"

if ! docker ps --format '{{.Names}}' | grep -qx portainer; then
  echo "ERROR: no hay ningun contenedor llamado 'portainer' en marcha." >&2
  echo "       Este script solo hace falta si usas Portainer detras del proxy (PORTAINER_DOMAIN)." >&2
  exit 1
fi

CID="$(docker compose ps -q caddy)"
if [ -z "$CID" ]; then
  echo "ERROR: el servicio 'caddy' no esta levantado. Ejecuta 'docker compose up -d' primero." >&2
  exit 1
fi

NET="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}{{"\n"}}{{end}}' "$CID" | head -n1)"
if [ -z "$NET" ]; then
  echo "ERROR: no se pudo determinar la red de Caddy." >&2
  exit 1
fi

if docker network inspect "$NET" -f '{{range .Containers}}{{.Name}} {{end}}' | tr ' ' '\n' | grep -qx portainer; then
  echo "OK: 'portainer' ya esta conectado a la red '$NET'. Nada que hacer."
else
  docker network connect "$NET" portainer
  echo "OK: 'portainer' conectado a la red '$NET'."
  echo "    Si el proxy seguia fallando, reinicia Caddy: docker compose restart caddy"
fi

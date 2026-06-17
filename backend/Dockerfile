# Base Debian explícita (bookworm) para builds reproducibles. El tag flotante seguía
# trayendo parches de Python, pero NO actualizaba los paquetes del SO publicados después
# de hornear la imagen base: ahí está el grueso de los hallazgos del escáner (Trivy/Grype).
#
# Para máxima reproducibilidad se puede fijar por digest, p. ej.:
#   FROM python:3.12-slim-bookworm@sha256:<digest>
# (obtener el digest con `docker buildx imagetools inspect python:3.12-slim-bookworm`).
FROM python:3.12-slim-bookworm

WORKDIR /app

# PYTHONPATH=/app hace importable el paquete `app` para alembic, uvicorn y el entrypoint
# (el layout plano no instala `app` en site-packages con `pip install .`).
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Parches de seguridad del SO: aplica las actualizaciones de Debian posteriores a la
# imagen base (reduce CVEs del sistema). Se instala `gosu` para bajar privilegios de forma
# segura en el entrypoint. Sin recomendados ni listas de apt en la capa final.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

# Usuario sin privilegios para ejecutar la aplicación (menor superficie ante una eventual RCE:
# el proceso no es root dentro del contenedor). El UID/GID es configurable como build-arg por si
# se quiere alinear con el propietario de los bind mounts del host (./data, ./media).
ARG APP_UID=10001
ARG APP_GID=10001
RUN groupadd -g "${APP_GID}" appuser \
    && useradd -m -u "${APP_UID}" -g "${APP_GID}" -s /usr/sbin/nologin appuser

# Dependencias primero (capa cacheable). Se actualizan pip/setuptools/wheel porque sus
# versiones antiguas son un hallazgo recurrente del escáner.
COPY pyproject.toml .
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install .

COPY . .
RUN mkdir -p /app/data /app/media \
    && chmod +x /app/entrypoint.sh \
    && chown -R appuser:appuser /app/data /app/media

# NO se fija `USER appuser` aquí: el entrypoint arranca como root SOLO para ajustar los
# permisos de los volúmenes montados y, acto seguido, baja privilegios a `appuser` con gosu.
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]

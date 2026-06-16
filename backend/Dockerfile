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
# imagen base (reduce CVEs del sistema). Sin recomendados ni listas de apt en la capa final.
RUN apt-get update \
    && apt-get upgrade -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Dependencias primero (capa cacheable). Se actualizan pip/setuptools/wheel porque sus
# versiones antiguas son un hallazgo recurrente del escáner.
COPY pyproject.toml .
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install .

COPY . .
RUN mkdir -p /app/data /app/media \
    && chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]

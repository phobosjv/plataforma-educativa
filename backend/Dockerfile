FROM python:3.12-slim
WORKDIR /app
# PYTHONPATH=/app hace importable el paquete `app` para alembic, uvicorn y el entrypoint
# (el layout plano no instala `app` en site-packages con `pip install .`).
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .
COPY . .
RUN mkdir -p /app/data /app/media
RUN chmod +x /app/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]

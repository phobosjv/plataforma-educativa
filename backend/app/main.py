"""Punto de entrada de la API. Solo composición y montaje de routers."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles

import app.bootstrap  # noqa: F401 — registra modelos ORM con Base.metadata
from app.shared.infrastructure.database import get_db
from app.config import settings
from app.shared.domain.base import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    NotFoundError,
)
from app.shared.infrastructure.scheduler import MaintenanceScheduler, volcar_visitas
from app.version import __version__

logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Arranca y detiene las tareas de mantenimiento (backups, purga, volcado de visitas)."""
    scheduler = MaintenanceScheduler(settings)
    scheduler.start()
    try:
        yield
    finally:
        await scheduler.stop()
        # Persistir el último lote de visitas acumuladas antes de apagar (no perderlas).
        if settings.analytics_enabled:
            await asyncio.to_thread(volcar_visitas)


app = FastAPI(title="Plataforma Educativa API", version=__version__, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_allow_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AuthenticationError)
async def _auth_error(_: object, exc: AuthenticationError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc)})


@app.exception_handler(AuthorizationError)
async def _authz_error(_: object, exc: AuthorizationError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(NotFoundError)
async def _not_found_error(_: object, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DomainError)
async def _domain_error(_: object, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


# Colores primarios de las paletas predefinidas (espejo de frontend/src/app/config/palettes.ts).
_PALETA_PRIMARY: dict[str, str] = {
    "cielo":    "#0284c7",
    "bosque":   "#2e7d32",
    "coral":    "#e91e63",
    "sol":      "#f59e0b",
    "lavanda":  "#9c27b0",
    "estandar": "#4f46e5",
}


@app.get("/manifest.webmanifest", tags=["infra"])
def pwa_manifest(db: Session = Depends(get_db)) -> Response:
    """Manifiesto PWA dinámico: nombre, iconos y color de la paleta activa."""
    from app.contexts.configuration.application.handlers import ObtenerConfiguracionHandler
    from app.contexts.configuration.infrastructure.repositories import (
        SqlAlchemyConfiguracionRepository,
    )

    cfg = ObtenerConfiguracionHandler(SqlAlchemyConfiguracionRepository(db)).handle()

    # Resolver color primario (paleta predefinida o personalizada).
    theme_color = _PALETA_PRIMARY.get(cfg.paleta_activa)
    if theme_color is None:
        for p in cfg.paletas_personalizadas:
            if p.id == cfg.paleta_activa:
                theme_color = p.primary
                break
    if theme_color is None:
        theme_color = "#0284c7"

    nombre = cfg.nombre_sitio
    short_name = nombre[:12]

    icons: list[dict[str, str]] = [
        {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
        {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ]
    if cfg.logo_url:
        icons.append({"src": cfg.logo_url, "sizes": "any"})

    manifest = {
        "name": nombre,
        "short_name": short_name,
        "description": "Plataforma educativa interactiva para infantil y primaria",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "orientation": "any",
        "background_color": "#ffffff",
        "theme_color": theme_color,
        "lang": "es",
        "categories": ["education", "kids"],
        "icons": icons,
    }
    return Response(
        content=json.dumps(manifest, ensure_ascii=False),
        media_type="application/manifest+json",
        headers={"Cache-Control": "no-cache"},
    )


class _NoSniffStaticFiles(StaticFiles):
    """Sirve ficheros estáticos forzando ``X-Content-Type-Options: nosniff``.

    Las imágenes subidas son raster (SVG está prohibido en la subida); el nosniff
    evita que el navegador interprete un fichero como un tipo distinto al declarado.
    """

    def file_response(self, *args: object, **kwargs: object) -> object:
        resp = super().file_response(*args, **kwargs)  # type: ignore[arg-type]
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp


_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


@app.get("/ficha/{file_hash}.pdf")
def servir_ficha_pdf_dev(
    file_hash: str, descargar: int = 0, nombre: str | None = None
) -> Response:
    """Sirve una ficha PDF desde el origen de la app.

    En dev: Vite proxea /ficha/ aquí, evitando la necesidad del servidor sandbox en :8002.
    En prod: pdf_base_url apunta al subdominio sandbox (nginx), este endpoint no se llega a usar.
    """
    if not _HASH_RE.match(file_hash):
        raise HTTPException(status_code=400, detail="Hash inválido.")
    ruta = Path(settings.media_dir) / file_hash[:2] / f"{file_hash}.pdf"
    if not ruta.is_file():
        raise HTTPException(status_code=404, detail="Ficha no encontrada.")
    if descargar:
        safe = "".join(c for c in (nombre or "") if c.isalnum() or c in " -_.").strip()
        safe_name = (safe[:100] or "ficha") + ".pdf"
        disposition = f'attachment; filename="{safe_name}"'
    else:
        disposition = "inline"
    return Response(
        content=ruta.read_bytes(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": disposition,
            "Cache-Control": "public, max-age=31536000, immutable",
            "Access-Control-Allow-Origin": "*",
        },
    )


# Imágenes de artículos: servidas desde el origen de la app (contenido seguro).
_images_dir = os.path.join(settings.media_dir, "images")
os.makedirs(_images_dir, exist_ok=True)
app.mount("/media/images", _NoSniffStaticFiles(directory=_images_dir), name="media-images")


# Routers por contexto
from app.contexts.identity.api.router import router as identity_router  # noqa: E402
from app.contexts.content.api.router import router as content_router  # noqa: E402
from app.contexts.taxonomy.api.router import router as taxonomy_router  # noqa: E402
from app.contexts.configuration.api.router import router as config_router  # noqa: E402
from app.contexts.media.api.router import router as media_router  # noqa: E402
from app.contexts.analytics.api.router import router as analytics_router  # noqa: E402
from app.contexts.auditing.api.router import router as auditing_router  # noqa: E402
from app.shared.api.maintenance_router import router as maintenance_router  # noqa: E402

app.include_router(identity_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(taxonomy_router, prefix="/api/v1")
app.include_router(config_router, prefix="/api/v1")
app.include_router(media_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(auditing_router, prefix="/api/v1")
app.include_router(maintenance_router, prefix="/api/v1")

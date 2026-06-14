"""Punto de entrada de la API. Solo composición y montaje de routers."""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

import app.bootstrap  # noqa: F401 — registra modelos ORM con Base.metadata
from app.config import settings
from app.shared.domain.base import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    NotFoundError,
)

logging.basicConfig(level=settings.log_level)

app = FastAPI(title="Plataforma Educativa API", version="0.8.0")

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


class _NoSniffStaticFiles(StaticFiles):
    """Sirve ficheros estáticos forzando ``X-Content-Type-Options: nosniff``.

    Las imágenes subidas son raster (SVG está prohibido en la subida); el nosniff
    evita que el navegador interprete un fichero como un tipo distinto al declarado.
    """

    def file_response(self, *args: object, **kwargs: object) -> object:
        resp = super().file_response(*args, **kwargs)  # type: ignore[arg-type]
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp


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

app.include_router(identity_router, prefix="/api/v1")
app.include_router(content_router, prefix="/api/v1")
app.include_router(taxonomy_router, prefix="/api/v1")
app.include_router(config_router, prefix="/api/v1")
app.include_router(media_router, prefix="/api/v1")

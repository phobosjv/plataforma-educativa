"""Caso de uso: guardar una imagen de artículo y devolver su URL.

Valida que sea una imagen RASTER permitida (sin SVG: un SVG podría contener script
y, servido desde el origen de la app, sería un vector XSS). Tamaño máximo acotado.
"""

from __future__ import annotations

from typing import Protocol

from app.shared.domain.base import DomainError

# content-type -> extensión de fichero. Deliberadamente SIN image/svg+xml.
TIPOS_PERMITIDOS: dict[str, str] = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
}

MAX_IMAGEN_BYTES = 5 * 1024 * 1024


class ImageStorage(Protocol):
    def save(self, raw: bytes, ext: str) -> str: ...


class GuardarImagenHandler:
    def __init__(self, storage: ImageStorage) -> None:
        self._storage = storage

    def handle(self, raw: bytes, content_type: str | None) -> str:
        if not raw:
            raise DomainError("La imagen está vacía.")
        if len(raw) > MAX_IMAGEN_BYTES:
            raise DomainError(
                f"La imagen supera el máximo de {MAX_IMAGEN_BYTES // (1024 * 1024)} MB."
            )
        ext = TIPOS_PERMITIDOS.get((content_type or "").split(";")[0].strip().lower())
        if ext is None:
            raise DomainError("Formato de imagen no permitido (usa PNG, JPG, GIF o WebP).")
        return self._storage.save(raw, ext)

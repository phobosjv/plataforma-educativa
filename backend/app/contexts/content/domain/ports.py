"""Puertos (interfaces) del contexto CONTENIDO. Los implementa la infraestructura."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.contexts.content.domain.model import Contenido, ContentVersion


class ContenidoRepository(Protocol):
    def add(self, contenido: Contenido) -> None: ...
    def get(self, contenido_id: UUID) -> Contenido | None: ...
    def save(self, contenido: Contenido) -> None: ...
    def list_published(self) -> list[Contenido]: ...
    def list_all(self) -> list[Contenido]: ...
    def list_trash(self) -> list[Contenido]: ...
    def delete_permanent(self, contenido_id: UUID) -> None: ...


class ContentVersionRepository(Protocol):
    def add(self, version: ContentVersion) -> None: ...
    def list_for_contenido(self, contenido_id: UUID) -> list[ContentVersion]: ...


class HtmlStorage(Protocol):
    """Almacén de ficheros HTML direccionado por hash SHA-256 (inmutable)."""

    def save(self, raw_html: bytes) -> str: ...  # devuelve el hash
    def url_for(self, file_hash: str) -> str: ...


class HtmlSanitizer(Protocol):
    """Sanea el HTML de los artículos de texto (whitelist de etiquetas seguras).

    Se aplica SIEMPRE al ``body_html`` de los contenidos de tipo ``texto`` antes de
    persistirlos (CLAUDE.md §10: sanitización del HTML de artículos en servidor). El
    HTML de ejercicios interactivos NO pasa por aquí: se aísla por iframe sandbox.
    """

    def sanitize(self, html: str) -> str: ...

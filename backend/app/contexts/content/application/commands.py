"""Comandos (escritura) del contexto CONTENIDO."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CrearContenidoCommand:
    titulo: str
    tipo: str
    autor_id: UUID
    descripcion: str = ""
    idioma: str = "es"
    etiquetas: tuple[str, ...] = ()
    ciclo_id: UUID | None = None
    curso_id: UUID | None = None
    asignatura_id: UUID | None = None
    body_html: str | None = None


@dataclass(frozen=True)
class ActualizarContenidoCommand:
    contenido_id: UUID
    editor_id: UUID
    titulo: str | None = None
    descripcion: str | None = None
    body_html: str | None = None
    etiquetas: tuple[str, ...] | None = None


@dataclass(frozen=True)
class SubirHtmlContenidoCommand:
    contenido_id: UUID
    editor_id: UUID
    raw_html: bytes


@dataclass(frozen=True)
class PublicarContenidoCommand:
    contenido_id: UUID
    published_by: UUID


@dataclass(frozen=True)
class ArchivarContenidoCommand:
    contenido_id: UUID


@dataclass(frozen=True)
class BorrarContenidoCommand:
    contenido_id: UUID
    deleted_by: UUID


@dataclass(frozen=True)
class RestaurarContenidoCommand:
    contenido_id: UUID
    restored_by: UUID

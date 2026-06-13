"""Modelo de dominio del contexto CONTENIDO (lenguaje ubicuo en español).

El dominio es PURO: nada de FastAPI ni SQLAlchemy aquí.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from app.shared.domain.base import DomainError, DomainEvent, Entity, new_id, now


class TipoContenido(str, Enum):
    INTERACTIVO = "interactivo"  # fichero HTML autocontenido (ejecuta JS, va aislado)
    TEXTO = "texto"  # artículo WYSIWYG (HTML sanitizado)


# --- Eventos de dominio ---


@dataclass(frozen=True)
class ContenidoCreado(DomainEvent):
    contenido_id: UUID = field(default_factory=lambda: UUID(int=0))


@dataclass(frozen=True)
class ContenidoPublicado(DomainEvent):
    contenido_id: UUID = field(default_factory=lambda: UUID(int=0))


@dataclass(frozen=True)
class ContenidoBorrado(DomainEvent):
    contenido_id: UUID = field(default_factory=lambda: UUID(int=0))


@dataclass(frozen=True)
class ContenidoRestaurado(DomainEvent):
    contenido_id: UUID = field(default_factory=lambda: UUID(int=0))


# --- Snapshot inmutable de versión ---


@dataclass(frozen=True)
class ContentVersion:
    """Snapshot inmutable del estado de Contenido en el momento de cada modificación."""

    contenido_id: UUID
    version_no: int
    metadata_snapshot: dict[str, Any]
    created_by: UUID
    id: UUID = field(default_factory=new_id)
    body_html: str | None = None
    hash_html: str | None = None
    created_at: datetime = field(default_factory=now)


# --- Agregado principal ---


@dataclass
class Contenido(Entity):
    titulo: str = ""
    descripcion: str = ""
    autor_id: UUID | None = None
    tipo: TipoContenido = TipoContenido.INTERACTIVO
    ciclo_id: UUID | None = None
    curso_id: UUID | None = None
    asignatura_id: UUID | None = None
    idioma: str = "es"
    etiquetas: list[str] = field(default_factory=list)
    publicado: bool = False
    borrado: bool = False
    hash_html: str | None = None  # solo para INTERACTIVO
    body_html: str | None = None  # solo para TEXTO
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if not self.titulo.strip():
            raise DomainError("El contenido requiere un título.")

    def publicar(self) -> ContenidoPublicado:
        if self.borrado:
            raise DomainError("No se puede publicar un contenido borrado.")
        self.publicado = True
        return ContenidoPublicado(contenido_id=self.id)

    def archivar(self) -> None:
        self.publicado = False

    def borrar(self) -> ContenidoBorrado:
        self.publicado = False
        self.borrado = True
        return ContenidoBorrado(contenido_id=self.id)

    def restaurar(self) -> ContenidoRestaurado:
        self.borrado = False
        return ContenidoRestaurado(contenido_id=self.id)

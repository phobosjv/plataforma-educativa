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
    PDF = "pdf"  # ficha PDF imprimible/descargable (se sirve aislada, no se sanea)


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
    hash_pdf: str | None = None
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
    hash_pdf: str | None = None  # solo para PDF (fichero PDF por hash, inmutable)
    # Marca de "simulacro de examen": solo aplica a ejercicios interactivos. En el catálogo,
    # los exámenes se listan al final y con un icono propio (la fusión de varios ejercicios en
    # uno la hace a mano el diseñador; aquí es solo una marca para ordenar y distinguir).
    es_examen: bool = False
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)

    def __post_init__(self) -> None:
        if not self.titulo.strip():
            raise DomainError("El contenido requiere un título.")
        if self.es_examen and self.tipo is not TipoContenido.INTERACTIVO:
            raise DomainError("Solo un ejercicio interactivo puede marcarse como examen.")

    def marcar_examen(self, valor: bool) -> None:
        """Marca o desmarca el contenido como examen (solo válido en interactivos)."""
        if valor and self.tipo is not TipoContenido.INTERACTIVO:
            raise DomainError("Solo un ejercicio interactivo puede marcarse como examen.")
        self.es_examen = valor

    def adjuntar_html_interactivo(self, file_hash: str) -> None:
        """Asocia el fichero HTML (por hash) a un ejercicio interactivo.

        Invariante de dominio: solo los contenidos de tipo ``interactivo`` referencian
        un fichero HTML; el de tipo ``texto`` guarda su cuerpo sanitizado en ``body_html``.
        """
        if self.tipo is not TipoContenido.INTERACTIVO:
            raise DomainError("Solo los contenidos interactivos admiten un fichero HTML.")
        if self.borrado:
            raise DomainError("No se puede adjuntar HTML a un contenido en la papelera.")
        self.hash_html = file_hash

    def adjuntar_pdf(self, file_hash: str) -> None:
        """Asocia el fichero PDF (por hash) a una ficha de tipo ``pdf``.

        Invariante de dominio: solo los contenidos de tipo ``pdf`` referencian un fichero PDF.
        El fichero es binario, content-addressed e inmutable; se sirve aislado (origen sandbox),
        por lo que NO se sanea (CLAUDE.md §10).
        """
        if self.tipo is not TipoContenido.PDF:
            raise DomainError("Solo los contenidos PDF admiten un fichero PDF.")
        if self.borrado:
            raise DomainError("No se puede adjuntar un PDF a un contenido en la papelera.")
        self.hash_pdf = file_hash

    def publicar(self) -> ContenidoPublicado:
        if self.borrado:
            raise DomainError("No se puede publicar un contenido borrado.")
        # Un ejercicio interactivo sin su fichero HTML mostraría una página vacía en público;
        # exigir el fichero evita publicar un ejercicio a medias.
        if self.tipo is TipoContenido.INTERACTIVO and not self.hash_html:
            raise DomainError("No se puede publicar un ejercicio interactivo sin su fichero HTML.")
        # Una ficha PDF sin su fichero no se podría ni ver ni descargar: misma exigencia.
        if self.tipo is TipoContenido.PDF and not self.hash_pdf:
            raise DomainError("No se puede publicar una ficha PDF sin su fichero.")
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

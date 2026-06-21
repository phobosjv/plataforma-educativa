"""DTOs de la capa de aplicación del contexto CONTENIDO (dataclasses puros)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.contexts.content.domain.model import ContentVersion, Contenido


@dataclass(frozen=True)
class ContenidoDTO:
    id: UUID
    titulo: str
    descripcion: str
    tipo: str
    autor_id: UUID | None
    publicado: bool
    borrado: bool
    es_examen: bool
    idioma: str
    etiquetas: tuple[str, ...]
    ciclo_id: UUID | None
    curso_id: UUID | None
    asignatura_id: UUID | None
    hash_html: str | None
    hash_pdf: str | None
    body_html: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class VersionDTO:
    version_no: int
    titulo: str
    tipo: str
    created_by: UUID
    created_at: datetime


def version_to_dto(v: ContentVersion) -> VersionDTO:
    snap = v.metadata_snapshot
    return VersionDTO(
        version_no=v.version_no,
        titulo=str(snap.get("titulo", "")),
        tipo=str(snap.get("tipo", "")),
        created_by=v.created_by,
        created_at=v.created_at,
    )


def contenido_to_dto(c: Contenido) -> ContenidoDTO:
    return ContenidoDTO(
        id=c.id,
        titulo=c.titulo,
        descripcion=c.descripcion,
        tipo=c.tipo.value,
        autor_id=c.autor_id,
        publicado=c.publicado,
        borrado=c.borrado,
        es_examen=c.es_examen,
        idioma=c.idioma,
        etiquetas=tuple(c.etiquetas),
        ciclo_id=c.ciclo_id,
        curso_id=c.curso_id,
        asignatura_id=c.asignatura_id,
        hash_html=c.hash_html,
        hash_pdf=c.hash_pdf,
        body_html=c.body_html,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )

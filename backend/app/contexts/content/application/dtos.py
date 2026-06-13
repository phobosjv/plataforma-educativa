"""DTOs de la capa de aplicación del contexto CONTENIDO (dataclasses puros)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.contexts.content.domain.model import Contenido


@dataclass(frozen=True)
class ContenidoDTO:
    id: UUID
    titulo: str
    descripcion: str
    tipo: str
    autor_id: UUID | None
    publicado: bool
    borrado: bool
    idioma: str
    etiquetas: tuple[str, ...]
    hash_html: str | None
    body_html: str | None
    created_at: datetime
    updated_at: datetime


def contenido_to_dto(c: Contenido) -> ContenidoDTO:
    return ContenidoDTO(
        id=c.id,
        titulo=c.titulo,
        descripcion=c.descripcion,
        tipo=c.tipo.value,
        autor_id=c.autor_id,
        publicado=c.publicado,
        borrado=c.borrado,
        idioma=c.idioma,
        etiquetas=tuple(c.etiquetas),
        hash_html=c.hash_html,
        body_html=c.body_html,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )

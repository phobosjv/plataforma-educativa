"""DTOs de la capa de aplicación del contexto AUDITING."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.contexts.auditing.domain.model import EntradaAuditoria


@dataclass(frozen=True)
class AuditoriaDTO:
    id: UUID
    usuario_id: UUID | None
    usuario_email: str
    usuario_rol: str
    accion: str
    entidad: str
    entidad_id: str | None
    detalle: str
    created_at: datetime


def entrada_to_dto(e: EntradaAuditoria) -> AuditoriaDTO:
    return AuditoriaDTO(
        id=e.id,
        usuario_id=e.usuario_id,
        usuario_email=e.usuario_email,
        usuario_rol=e.usuario_rol,
        accion=e.accion,
        entidad=e.entidad,
        entidad_id=e.entidad_id,
        detalle=e.detalle,
        created_at=e.created_at,
    )

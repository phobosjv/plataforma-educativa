"""DTOs de la capa de aplicación (dataclasses puros, sin Pydantic)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.contexts.identity.domain.model import Usuario


@dataclass(frozen=True)
class UsuarioDTO:
    id: UUID
    email: str
    rol: str
    activo: bool
    created_at: datetime


def usuario_to_dto(u: Usuario) -> UsuarioDTO:
    return UsuarioDTO(
        id=u.id,
        email=u.email,
        rol=u.rol.value,
        activo=u.activo,
        created_at=u.created_at,
    )

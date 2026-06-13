"""Bloques base del dominio. SIN dependencias de framework ni de infraestructura."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


def new_id() -> UUID:
    return uuid4()


def now() -> datetime:
    return datetime.now(tz=timezone.utc)


class DomainError(Exception):
    """Error de negocio. La capa API lo traduce a una respuesta HTTP."""


class NotFoundError(DomainError):
    """Entidad no encontrada → 404."""


class AuthenticationError(DomainError):
    """Credenciales inválidas o token expirado → 401."""


class AuthorizationError(DomainError):
    """Acción no permitida para el rol actual → 403."""


@dataclass(frozen=True)
class DomainEvent:
    """Evento de dominio (en proceso). Usado por auditoría y analítica."""

    occurred_on: datetime = field(default_factory=now)


@dataclass
class Entity:
    id: UUID = field(default_factory=new_id)

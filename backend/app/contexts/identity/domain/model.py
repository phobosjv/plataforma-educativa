"""Modelo de dominio del contexto IDENTITY. SIN dependencias de framework ni infraestructura."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID

from app.shared.domain.base import DomainError, DomainEvent, Entity, now

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Rol(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"


@dataclass(frozen=True)
class UsuarioCreado(DomainEvent):
    usuario_id: UUID = field(default_factory=lambda: UUID(int=0))


@dataclass(frozen=True)
class PasswordCambiada(DomainEvent):
    usuario_id: UUID = field(default_factory=lambda: UUID(int=0))


@dataclass
class Usuario(Entity):
    email: str = ""
    hashed_password: str = ""
    rol: Rol = Rol.EDITOR
    activo: bool = True
    created_at: datetime = field(default_factory=now)

    @classmethod
    def crear(cls, email: str, hashed_password: str, rol: Rol) -> "Usuario":
        if not _EMAIL_RE.match(email):
            raise DomainError("Email inválido.")
        if not hashed_password:
            raise DomainError("La contraseña no puede estar vacía.")
        return cls(email=email, hashed_password=hashed_password, rol=rol)

    def cambiar_password(self, new_hash: str) -> PasswordCambiada:
        if not new_hash:
            raise DomainError("La nueva contraseña no puede estar vacía.")
        self.hashed_password = new_hash
        return PasswordCambiada(usuario_id=self.id)

    def desactivar(self) -> None:
        if not self.activo:
            raise DomainError("El usuario ya está inactivo.")
        self.activo = False

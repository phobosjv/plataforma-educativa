"""Puertos del contexto IDENTITY. Los implementa la infraestructura."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.contexts.identity.domain.model import Usuario


class UsuarioRepository(Protocol):
    def add(self, usuario: Usuario) -> None: ...
    def get_by_id(self, usuario_id: UUID) -> Usuario | None: ...
    def get_by_email(self, email: str) -> Usuario | None: ...
    def list_all(self) -> list[Usuario]: ...

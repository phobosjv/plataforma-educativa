"""Queries (lectura) del contexto IDENTITY."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListarUsuariosQuery:
    pass


@dataclass(frozen=True)
class ObtenerUsuarioPorIdQuery:
    usuario_id: UUID

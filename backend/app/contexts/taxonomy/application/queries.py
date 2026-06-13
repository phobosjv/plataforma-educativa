"""Queries del contexto TAXONOMÍA."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ListarCiclosQuery:
    pass


@dataclass(frozen=True)
class ObtenerCicloQuery:
    ciclo_id: UUID


@dataclass(frozen=True)
class ListarCursosQuery:
    ciclo_id: UUID | None = None


@dataclass(frozen=True)
class ObtenerCursoQuery:
    curso_id: UUID


@dataclass(frozen=True)
class ListarAsignaturasQuery:
    pass


@dataclass(frozen=True)
class ObtenerAsignaturaQuery:
    asignatura_id: UUID

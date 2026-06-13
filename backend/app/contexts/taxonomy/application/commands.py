"""Comandos del contexto TAXONOMÍA."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CrearCicloCommand:
    nombre: str
    orden: int = 0


@dataclass(frozen=True)
class ActualizarCicloCommand:
    ciclo_id: UUID
    nombre: str | None = None
    orden: int | None = None


@dataclass(frozen=True)
class EliminarCicloCommand:
    ciclo_id: UUID


@dataclass(frozen=True)
class CrearCursoCommand:
    nombre: str
    ciclo_id: UUID
    orden: int = 0


@dataclass(frozen=True)
class ActualizarCursoCommand:
    curso_id: UUID
    nombre: str | None = None
    orden: int | None = None


@dataclass(frozen=True)
class EliminarCursoCommand:
    curso_id: UUID


@dataclass(frozen=True)
class CrearAsignaturaCommand:
    nombre: str
    color: str = "#6366f1"


@dataclass(frozen=True)
class ActualizarAsignaturaCommand:
    asignatura_id: UUID
    nombre: str | None = None
    color: str | None = None


@dataclass(frozen=True)
class EliminarAsignaturaCommand:
    asignatura_id: UUID

"""DTOs del contexto TAXONOMÍA."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.contexts.taxonomy.domain.model import Asignatura, Ciclo, Curso


@dataclass
class CicloDTO:
    id: UUID
    nombre: str
    orden: int


@dataclass
class CursoDTO:
    id: UUID
    nombre: str
    ciclo_id: UUID
    orden: int


@dataclass
class AsignaturaDTO:
    id: UUID
    nombre: str
    color: str


def ciclo_to_dto(c: Ciclo) -> CicloDTO:
    return CicloDTO(id=c.id, nombre=c.nombre, orden=c.orden)


def curso_to_dto(c: Curso) -> CursoDTO:
    assert c.ciclo_id is not None
    return CursoDTO(id=c.id, nombre=c.nombre, ciclo_id=c.ciclo_id, orden=c.orden)


def asignatura_to_dto(a: Asignatura) -> AsignaturaDTO:
    return AsignaturaDTO(id=a.id, nombre=a.nombre, color=a.color)

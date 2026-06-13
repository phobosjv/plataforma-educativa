"""Dominio del contexto TAXONOMÍA: Ciclo, Curso, Asignatura."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.shared.domain.base import DomainError, Entity


@dataclass
class Ciclo(Entity):
    """Etapa educativa (p. ej. Educación Infantil, 1er Ciclo de Primaria)."""

    nombre: str = ""
    orden: int = 0

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise DomainError("El nombre del ciclo no puede estar vacío.")

    def actualizar(self, nombre: str | None = None, orden: int | None = None) -> None:
        if nombre is not None:
            if not nombre.strip():
                raise DomainError("El nombre del ciclo no puede estar vacío.")
            self.nombre = nombre.strip()
        if orden is not None:
            self.orden = orden


@dataclass
class Curso(Entity):
    """Año académico dentro de un ciclo (p. ej. 1º Primaria)."""

    nombre: str = ""
    ciclo_id: UUID | None = None
    orden: int = 0

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise DomainError("El nombre del curso no puede estar vacío.")
        if self.ciclo_id is None:
            raise DomainError("El curso debe pertenecer a un ciclo.")

    def actualizar(self, nombre: str | None = None, orden: int | None = None) -> None:
        if nombre is not None:
            if not nombre.strip():
                raise DomainError("El nombre del curso no puede estar vacío.")
            self.nombre = nombre.strip()
        if orden is not None:
            self.orden = orden


@dataclass
class Asignatura(Entity):
    """Materia educativa (p. ej. Matemáticas, Lengua Castellana)."""

    nombre: str = ""
    color: str = "#6366f1"

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise DomainError("El nombre de la asignatura no puede estar vacío.")

    def actualizar(self, nombre: str | None = None, color: str | None = None) -> None:
        if nombre is not None:
            if not nombre.strip():
                raise DomainError("El nombre de la asignatura no puede estar vacío.")
            self.nombre = nombre.strip()
        if color is not None:
            self.color = color

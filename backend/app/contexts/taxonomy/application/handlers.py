"""Handlers de comandos y queries del contexto TAXONOMÍA."""

from __future__ import annotations

from uuid import UUID

from app.contexts.taxonomy.application.commands import (
    ActualizarAsignaturaCommand,
    ActualizarCicloCommand,
    ActualizarCursoCommand,
    CrearAsignaturaCommand,
    CrearCicloCommand,
    CrearCursoCommand,
    EliminarAsignaturaCommand,
    EliminarCicloCommand,
    EliminarCursoCommand,
)
from app.contexts.taxonomy.application.dtos import (
    AsignaturaDTO,
    CicloDTO,
    CursoDTO,
    asignatura_to_dto,
    ciclo_to_dto,
    curso_to_dto,
)
from app.contexts.taxonomy.application.queries import (
    ListarAsignaturasQuery,
    ListarCiclosQuery,
    ListarCursosQuery,
    ObtenerAsignaturaQuery,
    ObtenerCicloQuery,
    ObtenerCursoQuery,
)
from app.contexts.taxonomy.domain.model import Asignatura, Ciclo, Curso
from app.contexts.taxonomy.domain.ports import AsignaturaRepository, CicloRepository, CursoRepository
from app.shared.domain.base import NotFoundError
from app.shared.infrastructure.unit_of_work import UnitOfWork


# ── Ciclo ─────────────────────────────────────────────────────────────────────


class CrearCicloHandler:
    def __init__(self, repo: CicloRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: CrearCicloCommand) -> UUID:
        ciclo = Ciclo(nombre=cmd.nombre, orden=cmd.orden)
        self._repo.add(ciclo)
        self._uow.commit()
        return ciclo.id


class ActualizarCicloHandler:
    def __init__(self, repo: CicloRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: ActualizarCicloCommand) -> CicloDTO:
        ciclo = self._repo.get(cmd.ciclo_id)
        if ciclo is None:
            raise NotFoundError(f"Ciclo {cmd.ciclo_id} no encontrado.")
        ciclo.actualizar(nombre=cmd.nombre, orden=cmd.orden)
        self._repo.save(ciclo)
        self._uow.commit()
        return ciclo_to_dto(ciclo)


class EliminarCicloHandler:
    def __init__(self, repo: CicloRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: EliminarCicloCommand) -> None:
        if self._repo.get(cmd.ciclo_id) is None:
            raise NotFoundError(f"Ciclo {cmd.ciclo_id} no encontrado.")
        self._repo.delete(cmd.ciclo_id)
        self._uow.commit()


class ListarCiclosHandler:
    def __init__(self, repo: CicloRepository) -> None:
        self._repo = repo

    def handle(self, query: ListarCiclosQuery) -> list[CicloDTO]:
        return [ciclo_to_dto(c) for c in self._repo.list_all()]


class ObtenerCicloHandler:
    def __init__(self, repo: CicloRepository) -> None:
        self._repo = repo

    def handle(self, query: ObtenerCicloQuery) -> CicloDTO:
        ciclo = self._repo.get(query.ciclo_id)
        if ciclo is None:
            raise NotFoundError(f"Ciclo {query.ciclo_id} no encontrado.")
        return ciclo_to_dto(ciclo)


# ── Curso ─────────────────────────────────────────────────────────────────────


class CrearCursoHandler:
    def __init__(
        self, repo: CursoRepository, ciclo_repo: CicloRepository, uow: UnitOfWork
    ) -> None:
        self._repo = repo
        self._ciclo_repo = ciclo_repo
        self._uow = uow

    def handle(self, cmd: CrearCursoCommand) -> UUID:
        if self._ciclo_repo.get(cmd.ciclo_id) is None:
            raise NotFoundError(f"Ciclo {cmd.ciclo_id} no encontrado.")
        curso = Curso(nombre=cmd.nombre, ciclo_id=cmd.ciclo_id, orden=cmd.orden)
        self._repo.add(curso)
        self._uow.commit()
        return curso.id


class ActualizarCursoHandler:
    def __init__(self, repo: CursoRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: ActualizarCursoCommand) -> CursoDTO:
        curso = self._repo.get(cmd.curso_id)
        if curso is None:
            raise NotFoundError(f"Curso {cmd.curso_id} no encontrado.")
        curso.actualizar(nombre=cmd.nombre, orden=cmd.orden)
        self._repo.save(curso)
        self._uow.commit()
        return curso_to_dto(curso)


class EliminarCursoHandler:
    def __init__(self, repo: CursoRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: EliminarCursoCommand) -> None:
        if self._repo.get(cmd.curso_id) is None:
            raise NotFoundError(f"Curso {cmd.curso_id} no encontrado.")
        self._repo.delete(cmd.curso_id)
        self._uow.commit()


class ListarCursosHandler:
    def __init__(self, repo: CursoRepository) -> None:
        self._repo = repo

    def handle(self, query: ListarCursosQuery) -> list[CursoDTO]:
        items = (
            self._repo.list_by_ciclo(query.ciclo_id)
            if query.ciclo_id is not None
            else self._repo.list_all()
        )
        return [curso_to_dto(c) for c in items]


class ObtenerCursoHandler:
    def __init__(self, repo: CursoRepository) -> None:
        self._repo = repo

    def handle(self, query: ObtenerCursoQuery) -> CursoDTO:
        curso = self._repo.get(query.curso_id)
        if curso is None:
            raise NotFoundError(f"Curso {query.curso_id} no encontrado.")
        return curso_to_dto(curso)


# ── Asignatura ────────────────────────────────────────────────────────────────


class CrearAsignaturaHandler:
    def __init__(self, repo: AsignaturaRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: CrearAsignaturaCommand) -> UUID:
        asignatura = Asignatura(nombre=cmd.nombre, color=cmd.color)
        self._repo.add(asignatura)
        self._uow.commit()
        return asignatura.id


class ActualizarAsignaturaHandler:
    def __init__(self, repo: AsignaturaRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: ActualizarAsignaturaCommand) -> AsignaturaDTO:
        asignatura = self._repo.get(cmd.asignatura_id)
        if asignatura is None:
            raise NotFoundError(f"Asignatura {cmd.asignatura_id} no encontrada.")
        asignatura.actualizar(nombre=cmd.nombre, color=cmd.color)
        self._repo.save(asignatura)
        self._uow.commit()
        return asignatura_to_dto(asignatura)


class EliminarAsignaturaHandler:
    def __init__(self, repo: AsignaturaRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: EliminarAsignaturaCommand) -> None:
        if self._repo.get(cmd.asignatura_id) is None:
            raise NotFoundError(f"Asignatura {cmd.asignatura_id} no encontrada.")
        self._repo.delete(cmd.asignatura_id)
        self._uow.commit()


class ListarAsignaturasHandler:
    def __init__(self, repo: AsignaturaRepository) -> None:
        self._repo = repo

    def handle(self, query: ListarAsignaturasQuery) -> list[AsignaturaDTO]:
        return [asignatura_to_dto(a) for a in self._repo.list_all()]


class ObtenerAsignaturaHandler:
    def __init__(self, repo: AsignaturaRepository) -> None:
        self._repo = repo

    def handle(self, query: ObtenerAsignaturaQuery) -> AsignaturaDTO:
        asignatura = self._repo.get(query.asignatura_id)
        if asignatura is None:
            raise NotFoundError(f"Asignatura {query.asignatura_id} no encontrada.")
        return asignatura_to_dto(asignatura)

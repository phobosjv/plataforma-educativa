"""Repositorios SQLAlchemy del contexto TAXONOMÍA."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.contexts.taxonomy.domain.model import Asignatura, Ciclo, Curso
from app.contexts.taxonomy.infrastructure.models import AsignaturaModel, CicloModel, CursoModel


class SqlAlchemyCicloRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, ciclo: Ciclo) -> None:
        self._session.add(CicloModel(id=str(ciclo.id), nombre=ciclo.nombre, orden=ciclo.orden))

    def get(self, ciclo_id: UUID) -> Ciclo | None:
        m = self._session.get(CicloModel, str(ciclo_id))
        return self._to_domain(m) if m else None

    def save(self, ciclo: Ciclo) -> None:
        m = self._session.get(CicloModel, str(ciclo.id))
        if m:
            m.nombre = ciclo.nombre
            m.orden = ciclo.orden

    def delete(self, ciclo_id: UUID) -> None:
        m = self._session.get(CicloModel, str(ciclo_id))
        if m:
            self._session.delete(m)

    def list_all(self) -> list[Ciclo]:
        stmt = select(CicloModel).order_by(CicloModel.orden, CicloModel.nombre)
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    @staticmethod
    def _to_domain(m: CicloModel) -> Ciclo:
        return Ciclo(id=UUID(m.id), nombre=m.nombre, orden=m.orden)


class SqlAlchemyCursoRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, curso: Curso) -> None:
        self._session.add(
            CursoModel(
                id=str(curso.id),
                nombre=curso.nombre,
                ciclo_id=str(curso.ciclo_id),
                orden=curso.orden,
            )
        )

    def get(self, curso_id: UUID) -> Curso | None:
        m = self._session.get(CursoModel, str(curso_id))
        return self._to_domain(m) if m else None

    def save(self, curso: Curso) -> None:
        m = self._session.get(CursoModel, str(curso.id))
        if m:
            m.nombre = curso.nombre
            m.orden = curso.orden

    def delete(self, curso_id: UUID) -> None:
        m = self._session.get(CursoModel, str(curso_id))
        if m:
            self._session.delete(m)

    def list_all(self) -> list[Curso]:
        stmt = select(CursoModel).order_by(CursoModel.ciclo_id, CursoModel.orden, CursoModel.nombre)
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    def list_by_ciclo(self, ciclo_id: UUID) -> list[Curso]:
        stmt = (
            select(CursoModel)
            .where(CursoModel.ciclo_id == str(ciclo_id))
            .order_by(CursoModel.orden, CursoModel.nombre)
        )
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    @staticmethod
    def _to_domain(m: CursoModel) -> Curso:
        return Curso(id=UUID(m.id), nombre=m.nombre, ciclo_id=UUID(m.ciclo_id), orden=m.orden)


class SqlAlchemyAsignaturaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, asignatura: Asignatura) -> None:
        self._session.add(
            AsignaturaModel(id=str(asignatura.id), nombre=asignatura.nombre, color=asignatura.color)
        )

    def get(self, asignatura_id: UUID) -> Asignatura | None:
        m = self._session.get(AsignaturaModel, str(asignatura_id))
        return self._to_domain(m) if m else None

    def save(self, asignatura: Asignatura) -> None:
        m = self._session.get(AsignaturaModel, str(asignatura.id))
        if m:
            m.nombre = asignatura.nombre
            m.color = asignatura.color

    def delete(self, asignatura_id: UUID) -> None:
        m = self._session.get(AsignaturaModel, str(asignatura_id))
        if m:
            self._session.delete(m)

    def list_all(self) -> list[Asignatura]:
        stmt = select(AsignaturaModel).order_by(AsignaturaModel.nombre)
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    @staticmethod
    def _to_domain(m: AsignaturaModel) -> Asignatura:
        return Asignatura(id=UUID(m.id), nombre=m.nombre, color=m.color)

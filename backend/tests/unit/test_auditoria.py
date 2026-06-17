"""Tests del repositorio y handlers de AUDITING."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.bootstrap  # noqa: F401 — registra los modelos ORM
from app.contexts.auditing.application.handlers import ListarAuditoriaHandler
from app.contexts.auditing.domain.model import EntradaAuditoria
from app.contexts.auditing.infrastructure.repositories import SqlAlchemyAuditoriaRepository
from app.shared.infrastructure.database import Base
from app.shared.infrastructure.unit_of_work import UnitOfWork


@pytest.fixture()
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    s = sessionmaker(bind=engine)()
    try:
        yield s
    finally:
        s.close()
        Base.metadata.drop_all(engine)


def _entrada(accion: str, entidad: str = "contenido") -> EntradaAuditoria:
    return EntradaAuditoria(
        usuario_id=uuid4(),
        usuario_email="editor@test.es",
        usuario_rol="editor",
        accion=accion,
        entidad=entidad,
        entidad_id=str(uuid4()),
        detalle="Titulo X",
    )


def test_registrar_y_contar(session: Session) -> None:
    repo = SqlAlchemyAuditoriaRepository(session)
    repo.registrar(_entrada("crear"))
    repo.registrar(_entrada("publicar"))
    UnitOfWork(session).commit()
    assert repo.contar() == 2


def test_listar_mas_recientes_primero(session: Session) -> None:
    repo = SqlAlchemyAuditoriaRepository(session)
    for accion in ("crear", "editar", "borrar"):
        repo.registrar(_entrada(accion))
        UnitOfWork(session).commit()

    entradas, total = ListarAuditoriaHandler(repo).handle()
    assert total == 3
    # El ultimo registrado (borrar) debe aparecer primero.
    assert entradas[0].accion == "borrar"
    assert entradas[-1].accion == "crear"


def test_listar_respeta_limite_y_offset(session: Session) -> None:
    repo = SqlAlchemyAuditoriaRepository(session)
    for _ in range(5):
        repo.registrar(_entrada("crear"))
        UnitOfWork(session).commit()

    entradas, total = ListarAuditoriaHandler(repo).handle(limite=2, offset=1)
    assert total == 5
    assert len(entradas) == 2

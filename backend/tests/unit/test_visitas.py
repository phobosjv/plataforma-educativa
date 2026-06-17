"""Tests del contador de visitas: buffer en memoria + volcado por lotes + consulta."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.bootstrap  # noqa: F401 — registra los modelos ORM
from app.contexts.analytics.application.handlers import (
    ObtenerVisitasHandler,
    RegistrarVisitaHandler,
    VolcarVisitasHandler,
)
from app.contexts.analytics.infrastructure.buffer import BufferVisitasEnMemoria
from app.contexts.analytics.infrastructure.repositories import SqlAlchemyVisitasRepository
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


# ── Buffer en memoria ───────────────────────────────────────────────────────────


def test_buffer_acumula_y_drena() -> None:
    buffer = BufferVisitasEnMemoria()
    a, b = uuid4(), uuid4()
    buffer.registrar(a)
    buffer.registrar(a)
    buffer.registrar(b)
    assert buffer.pendientes() == 3

    drenado = buffer.drenar()
    assert drenado == {a: 2, b: 1}
    # Tras drenar, el buffer queda a cero.
    assert buffer.pendientes() == 0
    assert buffer.drenar() == {}


def test_registrar_visita_handler_usa_el_buffer() -> None:
    buffer = BufferVisitasEnMemoria()
    cid = uuid4()
    RegistrarVisitaHandler(buffer).handle(cid)
    assert buffer.drenar() == {cid: 1}


# ── Volcado por lotes ─────────────────────────────────────────────────────────


def test_volcar_persiste_y_vacia_el_buffer(session: Session) -> None:
    buffer = BufferVisitasEnMemoria()
    cid = uuid4()
    buffer.registrar(cid)
    buffer.registrar(cid)

    repo = SqlAlchemyVisitasRepository(session)
    n = VolcarVisitasHandler(buffer, repo, UnitOfWork(session)).handle()

    assert n == 2
    assert buffer.pendientes() == 0  # el buffer se drenó
    assert repo.total_por_contenido() == {cid: 2}


def test_volcar_sin_visitas_no_hace_nada(session: Session) -> None:
    buffer = BufferVisitasEnMemoria()
    repo = SqlAlchemyVisitasRepository(session)
    assert VolcarVisitasHandler(buffer, repo, UnitOfWork(session)).handle() == 0
    assert repo.total() == 0


def test_volcados_sucesivos_acumulan(session: Session) -> None:
    # El UPSERT debe SUMAR al total existente, no reemplazarlo.
    buffer = BufferVisitasEnMemoria()
    repo = SqlAlchemyVisitasRepository(session)
    cid = uuid4()

    buffer.registrar(cid)
    VolcarVisitasHandler(buffer, repo, UnitOfWork(session)).handle()
    buffer.registrar(cid)
    buffer.registrar(cid)
    VolcarVisitasHandler(buffer, repo, UnitOfWork(session)).handle()

    assert repo.total_por_contenido() == {cid: 3}


def test_obtener_visitas_devuelve_total_y_desglose(session: Session) -> None:
    buffer = BufferVisitasEnMemoria()
    repo = SqlAlchemyVisitasRepository(session)
    a, b = uuid4(), uuid4()
    buffer.registrar(a)
    buffer.registrar(b)
    buffer.registrar(b)
    VolcarVisitasHandler(buffer, repo, UnitOfWork(session)).handle()

    dto = ObtenerVisitasHandler(repo).handle()
    assert dto.total == 3
    assert dto.por_contenido == {a: 1, b: 2}

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
from uuid import UUID


class _ConocidosFake:
    """Doble del puerto ContenidosConocidos. ``todos=True`` acepta cualquier id; si no, solo
    los del conjunto dado."""

    def __init__(self, conocidos: set[UUID] | None = None, todos: bool = False) -> None:
        self._conocidos = conocidos or set()
        self._todos = todos

    def filtrar_existentes(self, ids: set[UUID]) -> set[UUID]:
        return set(ids) if self._todos else (set(ids) & self._conocidos)


_TODOS = _ConocidosFake(todos=True)


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
    n = VolcarVisitasHandler(buffer, repo, UnitOfWork(session), _TODOS).handle()

    assert n == 2
    assert buffer.pendientes() == 0  # el buffer se drenó
    assert repo.total_por_contenido() == {cid: 2}


def test_volcar_descarta_contenido_desconocido(session: Session) -> None:
    # Solo se persisten las visitas de contenido conocido; las de IDs desconocidos se descartan.
    buffer = BufferVisitasEnMemoria()
    repo = SqlAlchemyVisitasRepository(session)
    real, fantasma = uuid4(), uuid4()
    buffer.registrar(real)
    buffer.registrar(fantasma)
    buffer.registrar(fantasma)

    n = VolcarVisitasHandler(buffer, repo, UnitOfWork(session), _ConocidosFake({real})).handle()

    assert n == 1
    assert repo.total_por_contenido() == {real: 1}
    assert buffer.pendientes() == 0  # los descartados NO vuelven al buffer


def test_volcar_devuelve_al_buffer_si_falla_la_persistencia(session: Session) -> None:
    # Si la persistencia falla, el lote válido vuelve al buffer (no se pierde) y se relanza.
    class _RepoExplota:
        def incrementar(self, conteos: object) -> None:
            raise RuntimeError("BD caída")

        def total(self) -> int:
            return 0

        def total_por_contenido(self) -> dict:
            return {}

    buffer = BufferVisitasEnMemoria()
    cid = uuid4()
    buffer.registrar(cid)
    buffer.registrar(cid)

    with pytest.raises(RuntimeError):
        VolcarVisitasHandler(buffer, _RepoExplota(), UnitOfWork(session), _TODOS).handle()

    # El lote no se perdió: sigue en el buffer para el próximo intento.
    assert buffer.pendientes() == 2


def test_volcar_sin_visitas_no_hace_nada(session: Session) -> None:
    buffer = BufferVisitasEnMemoria()
    repo = SqlAlchemyVisitasRepository(session)
    assert VolcarVisitasHandler(buffer, repo, UnitOfWork(session), _TODOS).handle() == 0
    assert repo.total() == 0


def test_volcados_sucesivos_acumulan(session: Session) -> None:
    # El UPSERT debe SUMAR al total existente, no reemplazarlo.
    buffer = BufferVisitasEnMemoria()
    repo = SqlAlchemyVisitasRepository(session)
    cid = uuid4()

    buffer.registrar(cid)
    VolcarVisitasHandler(buffer, repo, UnitOfWork(session), _TODOS).handle()
    buffer.registrar(cid)
    buffer.registrar(cid)
    VolcarVisitasHandler(buffer, repo, UnitOfWork(session), _TODOS).handle()

    assert repo.total_por_contenido() == {cid: 3}


def test_obtener_visitas_devuelve_total_y_desglose(session: Session) -> None:
    buffer = BufferVisitasEnMemoria()
    repo = SqlAlchemyVisitasRepository(session)
    a, b = uuid4(), uuid4()
    buffer.registrar(a)
    buffer.registrar(b)
    buffer.registrar(b)
    VolcarVisitasHandler(buffer, repo, UnitOfWork(session), _TODOS).handle()

    dto = ObtenerVisitasHandler(repo).handle()
    assert dto.total == 3
    assert dto.por_contenido == {a: 1, b: 2}

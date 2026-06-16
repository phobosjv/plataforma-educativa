"""Tests del caso de uso de purga programada de la papelera y del filtro del repo."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.contexts.content.application.commands import PurgarPapeleraVencidaCommand
from app.contexts.content.application.handlers import PurgarPapeleraVencidaHandler
from app.contexts.content.domain.model import Contenido, TipoContenido
from app.contexts.content.infrastructure.repositories import SqlAlchemyContenidoRepository
from app.shared.infrastructure.database import Base
from app.shared.infrastructure.unit_of_work import UnitOfWork


# ── Handler (lógica de umbral y commit), con repo falso ──────────────────────────


class _FakeRepo:
    def __init__(self, vencidos: list[Contenido]) -> None:
        self._vencidos = vencidos
        self.limite_recibido: datetime | None = None
        self.borrados: list = []

    def list_trash_borrado_antes_de(self, limite: datetime) -> list[Contenido]:
        self.limite_recibido = limite
        return list(self._vencidos)

    def delete_permanent(self, contenido_id) -> None:  # noqa: ANN001
        self.borrados.append(contenido_id)


class _FakeUoW:
    def __init__(self) -> None:
        self.committed = False

    def commit(self) -> None:
        self.committed = True


def test_purga_elimina_los_vencidos_y_devuelve_el_conteo() -> None:
    vencidos = [
        Contenido(titulo="A", borrado=True),
        Contenido(titulo="B", borrado=True),
    ]
    repo, uow = _FakeRepo(vencidos), _FakeUoW()
    handler = PurgarPapeleraVencidaHandler(repo, uow)  # type: ignore[arg-type]

    n = handler.handle(PurgarPapeleraVencidaCommand(antiguedad_dias=30))

    assert n == 2
    assert repo.borrados == [vencidos[0].id, vencidos[1].id]
    assert uow.committed is True
    # El umbral es "ahora menos N días" (con margen de holgura por el tiempo de ejecución).
    esperado = datetime.now(tz=timezone.utc) - timedelta(days=30)
    assert repo.limite_recibido is not None
    assert abs((repo.limite_recibido - esperado).total_seconds()) < 60


def test_purga_sin_vencidos_no_hace_commit() -> None:
    repo, uow = _FakeRepo([]), _FakeUoW()
    handler = PurgarPapeleraVencidaHandler(repo, uow)  # type: ignore[arg-type]

    assert handler.handle(PurgarPapeleraVencidaCommand(antiguedad_dias=30)) == 0
    assert uow.committed is False


def test_purga_con_antiguedad_no_positiva_es_no_op() -> None:
    repo, uow = _FakeRepo([Contenido(titulo="A", borrado=True)]), _FakeUoW()
    handler = PurgarPapeleraVencidaHandler(repo, uow)  # type: ignore[arg-type]

    assert handler.handle(PurgarPapeleraVencidaCommand(antiguedad_dias=0)) == 0
    assert repo.borrados == []  # ni siquiera consulta la papelera
    assert uow.committed is False


# ── Filtro del repositorio contra SQLite real (en memoria) ───────────────────────


def _repo_en_memoria() -> tuple[SqlAlchemyContenidoRepository, object]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    return SqlAlchemyContenidoRepository(session), session


def test_repo_filtra_solo_papelera_mas_antigua_que_el_limite() -> None:
    repo, session = _repo_en_memoria()
    ahora = datetime.now(tz=timezone.utc)

    viejo_borrado = Contenido(
        titulo="Viejo en papelera", tipo=TipoContenido.TEXTO, borrado=True,
        updated_at=ahora - timedelta(days=40),
    )
    reciente_borrado = Contenido(
        titulo="Reciente en papelera", tipo=TipoContenido.TEXTO, borrado=True,
        updated_at=ahora - timedelta(days=5),
    )
    viejo_vivo = Contenido(
        titulo="Viejo pero NO borrado", tipo=TipoContenido.TEXTO, borrado=False,
        updated_at=ahora - timedelta(days=40),
    )
    for c in (viejo_borrado, reciente_borrado, viejo_vivo):
        repo.add(c)
    session.commit()

    limite = ahora - timedelta(days=30)
    vencidos = repo.list_trash_borrado_antes_de(limite)

    ids = {c.id for c in vencidos}
    assert ids == {viejo_borrado.id}  # solo el borrado y antiguo
    session.close()

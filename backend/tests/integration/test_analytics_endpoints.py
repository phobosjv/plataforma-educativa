"""Tests de integración del contador de visitas (contexto ANALYTICS)."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.contexts.analytics.application.handlers import VolcarVisitasHandler
from app.contexts.analytics.infrastructure.buffer import buffer_visitas
from app.contexts.analytics.infrastructure.repositories import SqlAlchemyVisitasRepository
from app.contexts.identity.domain.model import Rol, Usuario
from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
from app.main import app
from app.shared.infrastructure.database import Base, get_db
from app.shared.infrastructure.unit_of_work import UnitOfWork


@pytest.fixture(autouse=True)
def _buffer_limpio() -> Generator[None, None, None]:
    # El buffer es un singleton de proceso: vaciarlo antes de cada test aísla los conteos.
    buffer_visitas.drenar()
    yield
    buffer_visitas.drenar()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
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


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _token(db: Session, client: TestClient, email: str, rol: Rol) -> str:
    auth = ArgonAuthService("test-secret", 60)
    SqlAlchemyUsuarioRepository(db).add(Usuario.crear(email, auth.hash_password("password1"), rol))
    db.commit()
    r = client.post("/api/v1/auth/token", data={"username": email, "password": "password1"})
    return str(r.json()["access_token"])


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _volcar(db: Session) -> None:
    """Fuerza el volcado del buffer a la BD del test (lo que hace la tarea de fondo)."""
    VolcarVisitasHandler(buffer_visitas, SqlAlchemyVisitasRepository(db), UnitOfWork(db)).handle()


def test_registrar_visita_es_publico_y_no_escribe_en_bd(client: TestClient) -> None:
    cid = str(uuid4())
    r = client.post(f"/api/v1/analytics/visitas/{cid}")  # sin auth
    assert r.status_code == 204
    assert buffer_visitas.pendientes() == 1  # quedó en el buffer (en memoria)


def test_visitas_no_aparecen_hasta_el_volcado(
    client: TestClient, db_session: Session
) -> None:
    cid = str(uuid4())
    client.post(f"/api/v1/analytics/visitas/{cid}")
    admin = _token(db_session, client, "admin@test.es", Rol.ADMIN)

    # Antes del volcado, la BD no refleja nada.
    antes = client.get("/api/v1/analytics/visitas", headers=_h(admin)).json()
    assert antes["total"] == 0

    _volcar(db_session)

    despues = client.get("/api/v1/analytics/visitas", headers=_h(admin)).json()
    assert despues["total"] == 1
    assert despues["por_contenido"][cid] == 1


def test_varias_visitas_se_suman(client: TestClient, db_session: Session) -> None:
    cid = str(uuid4())
    for _ in range(3):
        client.post(f"/api/v1/analytics/visitas/{cid}")
    _volcar(db_session)
    admin = _token(db_session, client, "admin@test.es", Rol.ADMIN)
    body = client.get("/api/v1/analytics/visitas", headers=_h(admin)).json()
    assert body["total"] == 3
    assert body["por_contenido"][cid] == 3


def test_consultar_visitas_sin_auth_devuelve_401(client: TestClient) -> None:
    assert client.get("/api/v1/analytics/visitas").status_code == 401


def test_consultar_visitas_requiere_admin(client: TestClient, db_session: Session) -> None:
    editor = _token(db_session, client, "editor@test.es", Rol.EDITOR)
    assert client.get("/api/v1/analytics/visitas", headers=_h(editor)).status_code == 403


def test_registrar_visita_id_invalido_devuelve_422(client: TestClient) -> None:
    assert client.post("/api/v1/analytics/visitas/no-es-uuid").status_code == 422

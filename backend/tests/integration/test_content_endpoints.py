"""Tests de integración para los endpoints del contexto CONTENIDO."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.contexts.identity.domain.model import Rol, Usuario
from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
from app.main import app
from app.shared.infrastructure.database import Base, get_db

_TEST_DB_URL = "sqlite://"


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        _TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _create_user_and_token(db: Session, client: TestClient, email: str, rol: Rol) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db)
    usuario = Usuario.crear(email, auth.hash_password("password1"), rol)
    repo.add(usuario)
    db.commit()
    r = client.post("/api/v1/auth/token", data={"username": email, "password": "password1"})
    assert r.status_code == 200
    return str(r.json()["access_token"])


@pytest.fixture()
def editor_token(db_session: Session, client: TestClient) -> str:
    return _create_user_and_token(db_session, client, "editor@test.es", Rol.EDITOR)


@pytest.fixture()
def admin_token(db_session: Session, client: TestClient) -> str:
    return _create_user_and_token(db_session, client, "admin@test.es", Rol.ADMIN)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _crear_contenido(client: TestClient, token: str, titulo: str = "Test") -> dict:  # type: ignore[type-arg]
    r = client.post(
        "/api/v1/contenidos/",
        json={"titulo": titulo, "tipo": "texto", "body_html": "<p>hola</p>"},
        headers=_headers(token),
    )
    assert r.status_code == 201
    return r.json()  # type: ignore[no-any-return]


class TestContenidosPublicos:
    def test_listar_sin_auth_devuelve_200(self, client: TestClient) -> None:
        r = client.get("/api/v1/contenidos/")
        assert r.status_code == 200
        assert r.json() == []

    def test_no_muestra_no_publicados(self, client: TestClient, editor_token: str) -> None:
        _crear_contenido(client, editor_token)
        r = client.get("/api/v1/contenidos/")
        assert r.json() == []

    def test_muestra_publicados(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token, "Publicado")
        client.post(f"/api/v1/contenidos/{data['id']}/publicar", headers=_headers(editor_token))
        r = client.get("/api/v1/contenidos/")
        assert len(r.json()) == 1


class TestContenidoCRUD:
    def test_crear_sin_auth_devuelve_401(self, client: TestClient) -> None:
        r = client.post("/api/v1/contenidos/", json={"titulo": "X", "tipo": "texto"})
        assert r.status_code == 401

    def test_editor_puede_crear(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token)
        assert data["titulo"] == "Test"
        assert data["publicado"] is False

    def test_obtener_contenido_no_existe_devuelve_404(self, client: TestClient) -> None:
        r = client.get("/api/v1/contenidos/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_soft_delete_y_no_aparece_en_lista(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token)
        uid = data["id"]
        # Publicar → listar → borrar → listar
        client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(editor_token))
        r = client.get("/api/v1/contenidos/")
        assert len(r.json()) == 1

        client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))
        r = client.get("/api/v1/contenidos/")
        assert r.json() == []

    def test_restaurar_contenido(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token)
        uid = data["id"]
        client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))
        r = client.post(f"/api/v1/contenidos/{uid}/restaurar", headers=_headers(editor_token))
        assert r.status_code == 200
        assert r.json()["borrado"] is False

    def test_publicar_contenido(self, client: TestClient, editor_token: str) -> None:
        data = _crear_contenido(client, editor_token)
        uid = data["id"]
        r = client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(editor_token))
        assert r.status_code == 200
        assert r.json()["publicado"] is True


class TestAdminEndpoints:
    def test_admin_ve_papelera(
        self, client: TestClient, editor_token: str, admin_token: str
    ) -> None:
        data = _crear_contenido(client, editor_token)
        uid = data["id"]
        client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))

        r = client.get("/api/v1/admin/contenidos/", headers=_headers(admin_token))
        assert r.status_code == 200
        ids = [c["id"] for c in r.json()]
        assert uid in ids

    def test_editor_no_puede_acceder_admin(self, client: TestClient, editor_token: str) -> None:
        r = client.get("/api/v1/admin/contenidos/", headers=_headers(editor_token))
        assert r.status_code == 403

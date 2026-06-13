"""Tests de integración para los endpoints de autenticación y usuarios."""

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

_TEST_DB_URL = "sqlite://"  # en memoria


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
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin_token(db_session: Session, client: TestClient) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db_session)
    usuario = Usuario.crear("admin@test.es", auth.hash_password("password1"), Rol.ADMIN)
    repo.add(usuario)
    db_session.commit()

    r = client.post(
        "/api/v1/auth/token", data={"username": "admin@test.es", "password": "password1"}
    )
    assert r.status_code == 200
    return str(r.json()["access_token"])


@pytest.fixture()
def editor_token(db_session: Session, client: TestClient) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db_session)
    usuario = Usuario.crear("editor@test.es", auth.hash_password("password1"), Rol.EDITOR)
    repo.add(usuario)
    db_session.commit()

    r = client.post(
        "/api/v1/auth/token", data={"username": "editor@test.es", "password": "password1"}
    )
    assert r.status_code == 200
    return str(r.json()["access_token"])


class TestTokenEndpoint:
    def test_credenciales_validas_devuelve_token(self, admin_token: str) -> None:
        assert len(admin_token) > 10

    def test_password_incorrecta_devuelve_401(
        self, db_session: Session, client: TestClient
    ) -> None:
        auth = ArgonAuthService("test-secret", 60)
        repo = SqlAlchemyUsuarioRepository(db_session)
        repo.add(Usuario.crear("u@test.es", auth.hash_password("correcto"), Rol.EDITOR))
        db_session.commit()

        r = client.post(
            "/api/v1/auth/token", data={"username": "u@test.es", "password": "incorrecto"}
        )
        assert r.status_code == 401

    def test_usuario_inexistente_devuelve_401(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/auth/token", data={"username": "nadie@test.es", "password": "pass"}
        )
        assert r.status_code == 401


class TestUsersEndpoints:
    def test_listar_sin_token_devuelve_401(self, client: TestClient) -> None:
        r = client.get("/api/v1/users/")
        assert r.status_code == 401

    def test_listar_con_editor_devuelve_403(self, client: TestClient, editor_token: str) -> None:
        r = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {editor_token}"})
        assert r.status_code == 403

    def test_listar_con_admin_devuelve_200(self, client: TestClient, admin_token: str) -> None:
        r = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {admin_token}"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_crear_usuario_como_admin(self, client: TestClient, admin_token: str) -> None:
        r = client.post(
            "/api/v1/users/",
            json={"email": "nuevo@test.es", "password": "password1", "rol": "editor"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert r.status_code == 201
        assert "id" in r.json()

    def test_crear_usuario_sin_token_devuelve_401(self, client: TestClient) -> None:
        r = client.post(
            "/api/v1/users/",
            json={"email": "x@test.es", "password": "password1", "rol": "editor"},
        )
        assert r.status_code == 401

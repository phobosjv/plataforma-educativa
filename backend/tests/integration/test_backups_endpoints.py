"""Tests de integración de los endpoints admin de copias de seguridad."""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.contexts.identity.domain.model import Rol, Usuario
from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
from app.main import app
from app.shared.infrastructure.database import Base, get_db


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False)()
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


@pytest.fixture()
def backup_tmp(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Apunta el servicio de backup a una BD y un directorio temporales."""
    db = tmp_path / "app.sqlite3"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY)")
    con.commit()
    con.close()
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{db}")
    monkeypatch.setattr(settings, "backup_dir", str(tmp_path / "backups"))
    return tmp_path


@pytest.fixture()
def admin_token(db_session: Session, client: TestClient) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db_session)
    repo.add(Usuario.crear("admin@test.es", auth.hash_password("password1"), Rol.ADMIN))
    db_session.commit()
    resp = client.post(
        "/api/v1/auth/token", data={"username": "admin@test.es", "password": "password1"}
    )
    return resp.json()["access_token"]


@pytest.fixture()
def editor_token(db_session: Session, client: TestClient) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db_session)
    repo.add(Usuario.crear("editor@test.es", auth.hash_password("password1"), Rol.EDITOR))
    db_session.commit()
    resp = client.post(
        "/api/v1/auth/token", data={"username": "editor@test.es", "password": "password1"}
    )
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_listar_backups_requiere_autenticacion(client: TestClient) -> None:
    assert client.get("/api/v1/admin/backups").status_code == 401


def test_editor_no_puede_acceder_a_backups(client: TestClient, editor_token: str) -> None:
    assert client.get("/api/v1/admin/backups", headers=_auth(editor_token)).status_code == 403


def test_crear_y_listar_backup(
    client: TestClient, admin_token: str, backup_tmp: Path
) -> None:
    # Sin copias al principio.
    assert client.get("/api/v1/admin/backups", headers=_auth(admin_token)).json() == []

    creado = client.post("/api/v1/admin/backups", headers=_auth(admin_token))
    assert creado.status_code == 201
    cuerpo = creado.json()
    assert cuerpo["nombre"].startswith("app-")
    assert cuerpo["tamano_bytes"] > 0

    lista = client.get("/api/v1/admin/backups", headers=_auth(admin_token)).json()
    assert [b["nombre"] for b in lista] == [cuerpo["nombre"]]
    assert (backup_tmp / "backups" / cuerpo["nombre"]).exists()


def test_crear_backup_requiere_admin(client: TestClient, editor_token: str) -> None:
    assert client.post("/api/v1/admin/backups", headers=_auth(editor_token)).status_code == 403

"""Tests de integración de los endpoints de CONFIGURATION (apariencia/paletas)."""

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


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    # autoflush=False para igualar la SessionLocal de producción: con autoflush
    # activo, un session.get() forzaría el flush de objetos pendientes y el bug
    # del doble INSERT del singleton no se manifestaría (test inútil).
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
def admin_token(db_session: Session, client: TestClient) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db_session)
    usuario = Usuario.crear("admin@test.es", auth.hash_password("password1"), Rol.ADMIN)
    repo.add(usuario)
    db_session.commit()

    resp = client.post(
        "/api/v1/auth/token",
        data={"username": "admin@test.es", "password": "password1"},
    )
    return resp.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


PALETA = {
    "id": "bosque",
    "nombre": "Bosque",
    "bg": "#f0fdf4",
    "surface": "#ffffff",
    "fg": "#14532d",
    "primary": "#16a34a",
}


# ── Lectura pública ─────────────────────────────────────────────────────────────


def test_obtener_configuracion_crea_singleton_con_defaults(client: TestClient) -> None:
    """GET sobre la BD vacía devuelve la configuración por defecto sin error."""
    resp = client.get("/api/v1/config/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["paleta_activa"] == "cielo"
    assert body["paletas_personalizadas"] == []


# ── Activar paleta (regresión del 500) ──────────────────────────────────────────


def test_activar_paleta_sin_fila_singleton_previa(
    client: TestClient, admin_token: str
) -> None:
    """Regresión: activar una paleta cuando la fila singleton aún NO existe.

    Antes fallaba con 500 (IntegrityError por doble INSERT del mismo PK): ``get``
    añadía un modelo pendiente y ``save``, al no encontrarlo (autoflush=False),
    creaba un segundo modelo con el mismo id. La unificación en
    ``_get_or_create_model`` + ``flush`` lo evita.
    """
    resp = client.put(
        "/api/v1/config/paleta",
        json={"paleta_id": "atardecer"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["paleta_activa"] == "atardecer"

    # Persistió: una segunda lectura ve la paleta activa nueva.
    assert client.get("/api/v1/config/").json()["paleta_activa"] == "atardecer"


def test_activar_paleta_requiere_admin(client: TestClient) -> None:
    resp = client.put("/api/v1/config/paleta", json={"paleta_id": "atardecer"})
    assert resp.status_code == 401


# ── Paletas personalizadas ──────────────────────────────────────────────────────


def test_agregar_paleta_personalizada(client: TestClient, admin_token: str) -> None:
    resp = client.post(
        "/api/v1/config/paletas", json=PALETA, headers=auth_headers(admin_token)
    )
    assert resp.status_code == 201
    personalizadas = resp.json()["paletas_personalizadas"]
    assert len(personalizadas) == 1
    assert personalizadas[0]["id"] == "bosque"
    assert personalizadas[0]["primary"] == "#16a34a"


def test_agregar_paleta_duplicada_devuelve_error(
    client: TestClient, admin_token: str
) -> None:
    client.post("/api/v1/config/paletas", json=PALETA, headers=auth_headers(admin_token))
    resp = client.post(
        "/api/v1/config/paletas", json=PALETA, headers=auth_headers(admin_token)
    )
    assert resp.status_code == 400


def test_eliminar_paleta_personalizada(client: TestClient, admin_token: str) -> None:
    client.post("/api/v1/config/paletas", json=PALETA, headers=auth_headers(admin_token))

    resp = client.delete(
        "/api/v1/config/paletas/bosque", headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    assert resp.json()["paletas_personalizadas"] == []


def test_no_se_puede_eliminar_la_paleta_activa(
    client: TestClient, admin_token: str
) -> None:
    client.post("/api/v1/config/paletas", json=PALETA, headers=auth_headers(admin_token))
    client.put(
        "/api/v1/config/paleta",
        json={"paleta_id": "bosque"},
        headers=auth_headers(admin_token),
    )

    resp = client.delete(
        "/api/v1/config/paletas/bosque", headers=auth_headers(admin_token)
    )
    assert resp.status_code == 400

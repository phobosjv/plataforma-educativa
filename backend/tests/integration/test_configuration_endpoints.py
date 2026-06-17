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
    assert body["fuente_activa"] == "sistema"
    assert body["paletas_personalizadas"] == []


# ── Ajustes generales: nombre del sitio + fuente ────────────────────────────────


def test_actualizar_ajustes_generales(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "Cole San José", "fuente_activa": "nunito"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["nombre_sitio"] == "Cole San José"
    assert body["fuente_activa"] == "nunito"

    # Persiste y se ve en una segunda lectura pública.
    publico = client.get("/api/v1/config/").json()
    assert publico["nombre_sitio"] == "Cole San José"
    assert publico["fuente_activa"] == "nunito"


def test_obtener_configuracion_incluye_fondo_por_defecto(client: TestClient) -> None:
    body = client.get("/api/v1/config/").json()
    assert body["fondo_activo"] == "ninguno"


def test_aula_abierta_por_defecto(client: TestClient) -> None:
    body = client.get("/api/v1/config/").json()
    assert body["aula_abierta_label"] == "Aula Abierta"
    assert body["aula_abierta_emoji"] == "🌟"


def test_actualizar_aula_abierta(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={
            "nombre_sitio": "Mi Cole",
            "fuente_activa": "sistema",
            "aula_abierta_label": "Diversidad",
            "aula_abierta_emoji": "🌈",
        },
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["aula_abierta_label"] == "Diversidad"
    assert resp.json()["aula_abierta_emoji"] == "🌈"
    publico = client.get("/api/v1/config/").json()
    assert publico["aula_abierta_label"] == "Diversidad"


def test_aula_abierta_label_vacio_devuelve_error(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "Mi Cole", "fuente_activa": "sistema", "aula_abierta_label": "   "},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


def test_logo_url_por_defecto_vacio(client: TestClient) -> None:
    assert client.get("/api/v1/config/").json()["logo_url"] == ""


def test_actualizar_logo(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={
            "nombre_sitio": "Mi Cole",
            "fuente_activa": "sistema",
            "logo_url": "/media/images/abc123.png",
        },
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["logo_url"] == "/media/images/abc123.png"
    assert client.get("/api/v1/config/").json()["logo_url"] == "/media/images/abc123.png"


def test_quitar_logo_con_cadena_vacia(client: TestClient, admin_token: str) -> None:
    client.put(
        "/api/v1/config/general",
        json={
            "nombre_sitio": "Mi Cole",
            "fuente_activa": "sistema",
            "logo_url": "/media/images/abc123.png",
        },
        headers=auth_headers(admin_token),
    )
    resp = client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "Mi Cole", "fuente_activa": "sistema", "logo_url": ""},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["logo_url"] == ""


def test_logo_externo_rechazado(client: TestClient, admin_token: str) -> None:
    # Solo se admiten referencias al propio origen (/media/...): jamás una URL externa
    # que filtraría la IP de los menores a terceros (CLAUDE.md §10).
    resp = client.put(
        "/api/v1/config/general",
        json={
            "nombre_sitio": "Mi Cole",
            "fuente_activa": "sistema",
            "logo_url": "https://cdn.malo.example/logo.png",
        },
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


def test_actualizar_fondo(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "Mi Cole", "fuente_activa": "sistema", "fondo_activo": "classroom"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["fondo_activo"] == "classroom"
    assert client.get("/api/v1/config/").json()["fondo_activo"] == "classroom"


def test_fondo_no_permitido_devuelve_error(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "Mi Cole", "fuente_activa": "sistema", "fondo_activo": "discoteca"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


def test_fondo_estilo_por_defecto_es_ordenado(client: TestClient) -> None:
    assert client.get("/api/v1/config/").json()["fondo_estilo"] == "ordenado"


def test_actualizar_fondo_estilo_desordenado(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={
            "nombre_sitio": "Mi Cole",
            "fuente_activa": "sistema",
            "fondo_activo": "naturaleza",
            "fondo_estilo": "desordenado",
        },
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["fondo_estilo"] == "desordenado"
    assert client.get("/api/v1/config/").json()["fondo_estilo"] == "desordenado"


def test_fondo_estilo_no_permitido_devuelve_error(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={
            "nombre_sitio": "Mi Cole",
            "fuente_activa": "sistema",
            "fondo_activo": "naturaleza",
            "fondo_estilo": "caotico-total",
        },
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


def test_ajustes_generales_requiere_admin(client: TestClient) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "Sin permiso", "fuente_activa": "lexend"},
    )
    assert resp.status_code == 401


def test_fuente_no_permitida_devuelve_error(client: TestClient, admin_token: str) -> None:
    resp = client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "Mi Cole", "fuente_activa": "comic-sans-pirata"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


def test_nombre_vacio_devuelve_error(client: TestClient, admin_token: str) -> None:
    # Cadena no vacía para Pydantic pero vacía tras strip => DomainError (400).
    resp = client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "   ", "fuente_activa": "sistema"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


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

"""Tests de integración del buscador full-text (FTS5) del catálogo público.

La tabla virtual ``content_fts`` y sus triggers solo existen en la migración Alembic,
no en ``Base.metadata.create_all``. Por eso este fixture crea el índice de búsqueda a
mano (con el mismo DDL que usa la migración) tras montar el esquema, de modo que los
triggers estén activos cuando se inserte contenido.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.contexts.content.infrastructure.fts import crear_indice_busqueda
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
    # Índice FTS5 + triggers sobre la conexión cruda (compartida por StaticPool).
    raw = engine.raw_connection()
    try:
        crear_indice_busqueda(raw.dbapi_connection)
        raw.commit()
    finally:
        raw.close()
    session = sessionmaker(bind=engine)()
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
def editor_token(db_session: Session, client: TestClient) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db_session)
    repo.add(Usuario.crear("editor@test.es", auth.hash_password("password1"), Rol.EDITOR))
    db_session.commit()
    r = client.post("/api/v1/auth/token", data={"username": "editor@test.es", "password": "password1"})
    return str(r.json()["access_token"])


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _crear_publicado(
    client: TestClient, token: str, titulo: str, descripcion: str = "", etiquetas: list[str] | None = None
) -> str:
    r = client.post(
        "/api/v1/contenidos/",
        json={
            "titulo": titulo,
            "tipo": "texto",
            "descripcion": descripcion,
            "etiquetas": etiquetas or [],
        },
        headers=_headers(token),
    )
    assert r.status_code == 201, r.text
    uid = r.json()["id"]
    client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_headers(token))
    return str(uid)


def _buscar(client: TestClient, q: str) -> list[dict]:  # type: ignore[type-arg]
    r = client.get("/api/v1/contenidos/buscar", params={"q": q})
    assert r.status_code == 200, r.text
    return r.json()  # type: ignore[no-any-return]


def test_buscar_por_titulo_prefijo(client: TestClient, editor_token: str) -> None:
    uid = _crear_publicado(client, editor_token, "El mapa de las comunidades")
    _crear_publicado(client, editor_token, "Sumas y restas")
    res = _buscar(client, "mapa")
    assert [c["id"] for c in res] == [uid]


def test_buscar_es_publico_sin_auth(client: TestClient, editor_token: str) -> None:
    _crear_publicado(client, editor_token, "Los ríos de España")
    r = client.get("/api/v1/contenidos/buscar", params={"q": "rios"})  # sin token
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_buscar_ignora_acentos(client: TestClient, editor_token: str) -> None:
    # Indexado con tilde, se encuentra sin tilde (y viceversa): pensado para niños.
    _crear_publicado(client, editor_token, "Comunidades Autónomas de España")
    assert len(_buscar(client, "autonomas")) == 1
    assert len(_buscar(client, "españa")) == 1


def test_buscar_por_descripcion_y_etiqueta(client: TestClient, editor_token: str) -> None:
    _crear_publicado(
        client, editor_token, "Actividad uno",
        descripcion="repaso de fracciones", etiquetas=["matematicas", "primaria"],
    )
    assert len(_buscar(client, "fracciones")) == 1  # descripción
    assert len(_buscar(client, "matematicas")) == 1  # etiqueta


def test_buscar_varios_terminos_es_and(client: TestClient, editor_token: str) -> None:
    uid = _crear_publicado(client, editor_token, "El mapa de los ríos")
    _crear_publicado(client, editor_token, "El mapa político")
    # Ambos prefijos deben aparecer: solo el primero tiene "mapa" + "rio".
    assert [c["id"] for c in _buscar(client, "mapa rio")] == [uid]


def test_no_devuelve_no_publicados(client: TestClient, editor_token: str) -> None:
    r = client.post(
        "/api/v1/contenidos/",
        json={"titulo": "Borrador secreto", "tipo": "texto"},
        headers=_headers(editor_token),
    )
    assert r.status_code == 201  # creado pero NO publicado
    assert _buscar(client, "secreto") == []


def test_no_devuelve_borrados(client: TestClient, editor_token: str) -> None:
    uid = _crear_publicado(client, editor_token, "Texto borrable")
    assert len(_buscar(client, "borrable")) == 1
    client.delete(f"/api/v1/contenidos/{uid}", headers=_headers(editor_token))  # a papelera
    assert _buscar(client, "borrable") == []


def test_busqueda_se_actualiza_al_editar_titulo(client: TestClient, editor_token: str) -> None:
    # Prueba que el trigger AFTER UPDATE mantiene el índice sincronizado.
    uid = _crear_publicado(client, editor_token, "Titulo viejo")
    client.put(
        f"/api/v1/contenidos/{uid}",
        json={"titulo": "Titulo nuevo brillante"},
        headers=_headers(editor_token),
    )
    assert _buscar(client, "viejo") == []
    assert [c["id"] for c in _buscar(client, "brillante")] == [uid]


def test_query_vacia_devuelve_lista_vacia(client: TestClient, editor_token: str) -> None:
    _crear_publicado(client, editor_token, "Algo")
    assert _buscar(client, "") == []
    assert _buscar(client, "   ") == []


def test_query_sin_coincidencias(client: TestClient, editor_token: str) -> None:
    _crear_publicado(client, editor_token, "Geografía de Europa")
    assert _buscar(client, "dinosaurios") == []


def test_caracteres_especiales_no_rompen(client: TestClient, editor_token: str) -> None:
    # Operadores de FTS5 escritos por el usuario no deben provocar 500.
    _crear_publicado(client, editor_token, "Suma y resta")
    r = client.get("/api/v1/contenidos/buscar", params={"q": 'suma OR -"x" AND ('})
    assert r.status_code == 200

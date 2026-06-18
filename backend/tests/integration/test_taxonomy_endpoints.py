"""Tests de integración de los endpoints de TAXONOMÍA."""

from __future__ import annotations

from collections.abc import Generator
from uuid import uuid4

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


# ── Ciclos ────────────────────────────────────────────────────────────────────


def test_listar_ciclos_vacio(client: TestClient) -> None:
    resp = client.get("/api/v1/taxonomy/ciclos/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_crear_ciclo_requiere_admin(client: TestClient) -> None:
    resp = client.post("/api/v1/taxonomy/ciclos/", json={"nombre": "Infantil"})
    assert resp.status_code == 401


def test_crear_y_listar_ciclo(client: TestClient, admin_token: str) -> None:
    resp = client.post(
        "/api/v1/taxonomy/ciclos/",
        json={"nombre": "Educación Infantil", "orden": 0},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201
    ciclo_id = resp.json()["id"]

    lista = client.get("/api/v1/taxonomy/ciclos/").json()
    assert len(lista) == 1
    assert lista[0]["nombre"] == "Educación Infantil"

    detalle = client.get(f"/api/v1/taxonomy/ciclos/{ciclo_id}").json()
    assert detalle["nombre"] == "Educación Infantil"


def test_actualizar_ciclo(client: TestClient, admin_token: str) -> None:
    uid = client.post(
        "/api/v1/taxonomy/ciclos/",
        json={"nombre": "Infantil"},
        headers=auth_headers(admin_token),
    ).json()["id"]

    resp = client.put(
        f"/api/v1/taxonomy/ciclos/{uid}",
        json={"nombre": "1er Ciclo Primaria", "orden": 1},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "1er Ciclo Primaria"
    assert resp.json()["orden"] == 1


def test_eliminar_ciclo(client: TestClient, admin_token: str) -> None:
    uid = client.post(
        "/api/v1/taxonomy/ciclos/",
        json={"nombre": "A eliminar"},
        headers=auth_headers(admin_token),
    ).json()["id"]

    resp = client.delete(f"/api/v1/taxonomy/ciclos/{uid}", headers=auth_headers(admin_token))
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/taxonomy/ciclos/{uid}")
    assert resp.status_code == 404


def test_obtener_ciclo_inexistente(client: TestClient) -> None:
    resp = client.get(f"/api/v1/taxonomy/ciclos/{uuid4()}")
    assert resp.status_code == 404


# ── Cursos ────────────────────────────────────────────────────────────────────


def test_crear_curso_con_ciclo_valido(client: TestClient, admin_token: str) -> None:
    ciclo_id = client.post(
        "/api/v1/taxonomy/ciclos/",
        json={"nombre": "1er Ciclo"},
        headers=auth_headers(admin_token),
    ).json()["id"]

    resp = client.post(
        "/api/v1/taxonomy/cursos/",
        json={"nombre": "1º Primaria", "ciclo_id": ciclo_id, "orden": 1},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201

    lista = client.get(f"/api/v1/taxonomy/cursos/?ciclo_id={ciclo_id}").json()
    assert len(lista) == 1
    assert lista[0]["nombre"] == "1º Primaria"
    assert lista[0]["ciclo_id"] == ciclo_id


def test_crear_curso_ciclo_inexistente(client: TestClient, admin_token: str) -> None:
    resp = client.post(
        "/api/v1/taxonomy/cursos/",
        json={"nombre": "1º Primaria", "ciclo_id": str(uuid4())},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 400


def test_listar_cursos_todos(client: TestClient, admin_token: str) -> None:
    c1 = client.post(
        "/api/v1/taxonomy/ciclos/", json={"nombre": "Ciclo A"}, headers=auth_headers(admin_token)
    ).json()["id"]
    c2 = client.post(
        "/api/v1/taxonomy/ciclos/", json={"nombre": "Ciclo B"}, headers=auth_headers(admin_token)
    ).json()["id"]
    client.post(
        "/api/v1/taxonomy/cursos/",
        json={"nombre": "1º", "ciclo_id": c1},
        headers=auth_headers(admin_token),
    )
    client.post(
        "/api/v1/taxonomy/cursos/",
        json={"nombre": "2º", "ciclo_id": c2},
        headers=auth_headers(admin_token),
    )
    lista = client.get("/api/v1/taxonomy/cursos/").json()
    assert len(lista) == 2


# ── Asignaturas ───────────────────────────────────────────────────────────────


def test_crear_y_listar_asignatura(client: TestClient, admin_token: str) -> None:
    resp = client.post(
        "/api/v1/taxonomy/asignaturas/",
        json={"nombre": "Matemáticas", "color": "#3b82f6"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201

    lista = client.get("/api/v1/taxonomy/asignaturas/").json()
    assert len(lista) == 1
    assert lista[0]["color"] == "#3b82f6"
    assert lista[0]["transversal"] is False  # por defecto NO transversal


def test_crear_asignatura_transversal(client: TestClient, admin_token: str) -> None:
    resp = client.post(
        "/api/v1/taxonomy/asignaturas/",
        json={"nombre": "Audición y Lenguaje", "transversal": True},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 201
    lista = client.get("/api/v1/taxonomy/asignaturas/").json()
    assert lista[0]["transversal"] is True


def test_marcar_asignatura_como_transversal(client: TestClient, admin_token: str) -> None:
    uid = client.post(
        "/api/v1/taxonomy/asignaturas/",
        json={"nombre": "Pedagogía Terapéutica"},
        headers=auth_headers(admin_token),
    ).json()["id"]

    resp = client.put(
        f"/api/v1/taxonomy/asignaturas/{uid}",
        json={"transversal": True},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["transversal"] is True
    # Persiste y se ve en la lista.
    assert client.get("/api/v1/taxonomy/asignaturas/").json()[0]["transversal"] is True


def test_actualizar_asignatura(client: TestClient, admin_token: str) -> None:
    uid = client.post(
        "/api/v1/taxonomy/asignaturas/",
        json={"nombre": "Lengua"},
        headers=auth_headers(admin_token),
    ).json()["id"]

    resp = client.put(
        f"/api/v1/taxonomy/asignaturas/{uid}",
        json={"nombre": "Lengua Castellana", "color": "#ef4444"},
        headers=auth_headers(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["nombre"] == "Lengua Castellana"
    assert resp.json()["color"] == "#ef4444"


def test_eliminar_asignatura(client: TestClient, admin_token: str) -> None:
    uid = client.post(
        "/api/v1/taxonomy/asignaturas/",
        json={"nombre": "Temporal"},
        headers=auth_headers(admin_token),
    ).json()["id"]

    resp = client.delete(
        f"/api/v1/taxonomy/asignaturas/{uid}", headers=auth_headers(admin_token)
    )
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/taxonomy/asignaturas/{uid}")
    assert resp.status_code == 404


# ── Integridad referencial al borrar (no dejar referencias colgando) ────────────


def _crear_contenido(
    client: TestClient,
    token: str,
    *,
    curso_id: str | None = None,
    asignatura_id: str | None = None,
) -> str:
    body = {"titulo": "Ficha", "tipo": "texto", "body_html": "<p>x</p>"}
    if curso_id:
        body["curso_id"] = curso_id
    if asignatura_id:
        body["asignatura_id"] = asignatura_id
    r = client.post("/api/v1/contenidos/", json=body, headers=auth_headers(token))
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_no_elimina_ciclo_con_cursos(client: TestClient, admin_token: str) -> None:
    ciclo_id = client.post(
        "/api/v1/taxonomy/ciclos/", json={"nombre": "Primaria"}, headers=auth_headers(admin_token)
    ).json()["id"]
    client.post(
        "/api/v1/taxonomy/cursos/",
        json={"nombre": "1º", "ciclo_id": ciclo_id},
        headers=auth_headers(admin_token),
    )

    resp = client.delete(f"/api/v1/taxonomy/ciclos/{ciclo_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 409
    assert "curso" in resp.json()["detail"].lower()
    # El ciclo sigue existiendo (no se borró).
    assert client.get(f"/api/v1/taxonomy/ciclos/{ciclo_id}").status_code == 200


def test_no_elimina_curso_con_contenido(client: TestClient, admin_token: str) -> None:
    ciclo_id = client.post(
        "/api/v1/taxonomy/ciclos/", json={"nombre": "Primaria"}, headers=auth_headers(admin_token)
    ).json()["id"]
    curso_id = client.post(
        "/api/v1/taxonomy/cursos/",
        json={"nombre": "1º", "ciclo_id": ciclo_id},
        headers=auth_headers(admin_token),
    ).json()["id"]
    _crear_contenido(client, admin_token, curso_id=curso_id)

    resp = client.delete(f"/api/v1/taxonomy/cursos/{curso_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 409
    assert "contenido" in resp.json()["detail"].lower()
    assert client.get(f"/api/v1/taxonomy/cursos/{curso_id}").status_code == 200


def test_no_elimina_asignatura_con_contenido(client: TestClient, admin_token: str) -> None:
    asig_id = client.post(
        "/api/v1/taxonomy/asignaturas/",
        json={"nombre": "Mates"},
        headers=auth_headers(admin_token),
    ).json()["id"]
    _crear_contenido(client, admin_token, asignatura_id=asig_id)

    resp = client.delete(
        f"/api/v1/taxonomy/asignaturas/{asig_id}", headers=auth_headers(admin_token)
    )
    assert resp.status_code == 409
    assert "contenido" in resp.json()["detail"].lower()
    assert client.get(f"/api/v1/taxonomy/asignaturas/{asig_id}").status_code == 200


def test_elimina_curso_sin_contenido(client: TestClient, admin_token: str) -> None:
    ciclo_id = client.post(
        "/api/v1/taxonomy/ciclos/", json={"nombre": "Primaria"}, headers=auth_headers(admin_token)
    ).json()["id"]
    curso_id = client.post(
        "/api/v1/taxonomy/cursos/",
        json={"nombre": "Libre", "ciclo_id": ciclo_id},
        headers=auth_headers(admin_token),
    ).json()["id"]

    resp = client.delete(f"/api/v1/taxonomy/cursos/{curso_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 204
    assert client.get(f"/api/v1/taxonomy/cursos/{curso_id}").status_code == 404

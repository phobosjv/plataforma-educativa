"""Tests de integración de la auditoría: las acciones de gestión quedan registradas."""

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


def _auditoria(client: TestClient, admin: str) -> dict:  # type: ignore[type-arg]
    r = client.get("/api/v1/auditoria", headers=_h(admin))
    assert r.status_code == 200, r.text
    return r.json()  # type: ignore[no-any-return]


def test_crear_contenido_queda_auditado(client: TestClient, db_session: Session) -> None:
    editor = _token(db_session, client, "editor@test.es", Rol.EDITOR)
    admin = _token(db_session, client, "admin@test.es", Rol.ADMIN)

    r = client.post(
        "/api/v1/contenidos/",
        json={"titulo": "Mi articulo", "tipo": "texto"},
        headers=_h(editor),
    )
    uid = r.json()["id"]

    data = _auditoria(client, admin)
    crear = [e for e in data["entradas"] if e["accion"] == "crear" and e["entidad"] == "contenido"]
    assert len(crear) == 1
    assert crear[0]["entidad_id"] == uid
    assert crear[0]["detalle"] == "Mi articulo"
    assert crear[0]["usuario_email"] == "editor@test.es"
    assert crear[0]["usuario_rol"] == "editor"


def test_ciclo_de_vida_genera_varias_entradas(client: TestClient, db_session: Session) -> None:
    editor = _token(db_session, client, "editor@test.es", Rol.EDITOR)
    admin = _token(db_session, client, "admin@test.es", Rol.ADMIN)

    uid = client.post(
        "/api/v1/contenidos/", json={"titulo": "X", "tipo": "texto"}, headers=_h(editor)
    ).json()["id"]
    client.post(f"/api/v1/contenidos/{uid}/publicar", headers=_h(editor))
    client.delete(f"/api/v1/contenidos/{uid}", headers=_h(editor))

    acciones = [e["accion"] for e in _auditoria(client, admin)["entradas"]]
    # Mas recientes primero: borrar, publicar, crear.
    assert acciones[:3] == ["borrar", "publicar", "crear"]


def test_accion_de_taxonomia_se_audita(client: TestClient, db_session: Session) -> None:
    admin = _token(db_session, client, "admin@test.es", Rol.ADMIN)
    client.post("/api/v1/taxonomy/ciclos/", json={"nombre": "Primaria"}, headers=_h(admin))

    data = _auditoria(client, admin)
    ciclos = [e for e in data["entradas"] if e["entidad"] == "ciclo" and e["accion"] == "crear"]
    assert len(ciclos) == 1
    assert ciclos[0]["detalle"] == "Primaria"


def test_cambio_de_configuracion_se_audita(client: TestClient, db_session: Session) -> None:
    admin = _token(db_session, client, "admin@test.es", Rol.ADMIN)
    client.put(
        "/api/v1/config/general",
        json={"nombre_sitio": "Mi Cole", "fuente_activa": "sistema"},
        headers=_h(admin),
    )
    data = _auditoria(client, admin)
    assert any(e["entidad"] == "configuracion" and e["accion"] == "editar" for e in data["entradas"])


def test_auditoria_sin_auth_devuelve_401(client: TestClient) -> None:
    assert client.get("/api/v1/auditoria").status_code == 401


def test_auditoria_requiere_admin(client: TestClient, db_session: Session) -> None:
    editor = _token(db_session, client, "editor@test.es", Rol.EDITOR)
    assert client.get("/api/v1/auditoria", headers=_h(editor)).status_code == 403


def test_accion_fallida_no_se_audita(client: TestClient, db_session: Session) -> None:
    # Un borrado de un id inexistente (404) no debe dejar entrada de auditoria.
    editor = _token(db_session, client, "editor@test.es", Rol.EDITOR)
    admin = _token(db_session, client, "admin@test.es", Rol.ADMIN)
    client.delete(
        "/api/v1/contenidos/00000000-0000-0000-0000-000000000000", headers=_h(editor)
    )
    data = _auditoria(client, admin)
    assert all(e["accion"] != "borrar" for e in data["entradas"])

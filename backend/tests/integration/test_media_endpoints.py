"""Tests de integración del contexto MEDIA (subida de imágenes de artículos)."""

from __future__ import annotations

import base64
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

# PNG 1x1 transparente (mínimo válido).
_PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)


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
def editor_token(db_session: Session, client: TestClient) -> str:
    auth = ArgonAuthService("test-secret", 60)
    repo = SqlAlchemyUsuarioRepository(db_session)
    repo.add(Usuario.crear("editor@test.es", auth.hash_password("password1"), Rol.EDITOR))
    db_session.commit()
    r = client.post("/api/v1/auth/token", data={"username": "editor@test.es", "password": "password1"})
    return str(r.json()["access_token"])


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_subir_png_devuelve_url(
    client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    r = client.post(
        "/api/v1/media/imagenes",
        files={"fichero": ("gato.png", _PNG_1X1, "image/png")},
        headers=_headers(editor_token),
    )
    assert r.status_code == 200
    url = r.json()["url"]
    assert url.startswith("/media/images/")
    assert url.endswith(".png")
    # Se escribió content-addressed en disco.
    nombre = url.rsplit("/", 1)[1]
    assert (tmp_path / "images" / nombre).read_bytes() == _PNG_1X1


def test_subir_no_imagen_devuelve_400(
    client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    r = client.post(
        "/api/v1/media/imagenes",
        files={"fichero": ("malo.txt", b"hola", "text/plain")},
        headers=_headers(editor_token),
    )
    assert r.status_code == 400


def test_subir_svg_rechazado(
    client: TestClient, editor_token: str, tmp_path, monkeypatch  # type: ignore[no-untyped-def]
) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    r = client.post(
        "/api/v1/media/imagenes",
        files={"fichero": ("x.svg", b"<svg></svg>", "image/svg+xml")},
        headers=_headers(editor_token),
    )
    assert r.status_code == 400  # SVG no permitido (vector XSS)


def test_subir_imagen_sin_auth_devuelve_401(client: TestClient) -> None:
    r = client.post(
        "/api/v1/media/imagenes",
        files={"fichero": ("gato.png", _PNG_1X1, "image/png")},
    )
    assert r.status_code == 401

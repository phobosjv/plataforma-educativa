"""Tests de integración del endpoint GET /manifest.webmanifest (PWA)."""

from __future__ import annotations

import json
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.shared.infrastructure.database import Base, get_db


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False)

    def override_db() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_manifest_devuelve_json_valido(client: TestClient) -> None:
    r = client.get("/manifest.webmanifest")
    assert r.status_code == 200
    assert "application/manifest+json" in r.headers["content-type"]
    data = r.json()
    assert data["name"]
    assert data["start_url"] == "/"
    assert data["display"] == "standalone"
    assert isinstance(data["icons"], list)
    assert any(i["sizes"] == "192x192" for i in data["icons"])
    assert any(i["sizes"] == "512x512" for i in data["icons"])


def test_manifest_sin_cache(client: TestClient) -> None:
    r = client.get("/manifest.webmanifest")
    assert r.headers.get("cache-control") == "no-cache"


def test_manifest_color_paleta_predefinida(client: TestClient) -> None:
    """Con la paleta por defecto 'cielo', theme_color debe ser #0284c7."""
    r = client.get("/manifest.webmanifest")
    assert r.json()["theme_color"] == "#0284c7"


def test_manifest_nombre_por_defecto(client: TestClient) -> None:
    r = client.get("/manifest.webmanifest")
    assert r.json()["name"] == "Plataforma Educativa"

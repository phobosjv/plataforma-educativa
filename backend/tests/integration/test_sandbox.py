"""Tests del servidor del ORIGEN SANDBOX (CLAUDE.md §10 / ARCHITECTURE AD-3).

Verifican que los HTML de ejercicios se sirven con CSP estricta y que el contenido
no se transforma, además del manejo de hash inválido / fichero inexistente.
"""

from __future__ import annotations

import hashlib

from fastapi.testclient import TestClient

from app.config import settings
from app.sandbox import sandbox_app


def _guardar_ejercicio(media_dir: str, raw: bytes) -> str:
    file_hash = hashlib.sha256(raw).hexdigest()
    destino = f"{media_dir}/{file_hash[:2]}"
    import os

    os.makedirs(destino, exist_ok=True)
    with open(f"{destino}/{file_hash}.html", "wb") as f:
        f.write(raw)
    return file_hash


def test_sirve_ejercicio_con_csp_estricta(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    raw = b"<html><body><script>1</script></body></html>"
    h = _guardar_ejercicio(str(tmp_path), raw)

    client = TestClient(sandbox_app)
    r = client.get(f"/ejercicio/{h}")

    assert r.status_code == 200
    assert r.content == raw  # NO se transforma
    csp = r.headers["content-security-policy"]
    assert "connect-src 'none'" in csp  # el ejercicio no puede llamar a casa
    assert "frame-ancestors" in csp  # solo la app puede embeberlo
    assert "default-src 'none'" in csp
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["referrer-policy"] == "no-referrer"


def test_hash_invalido_devuelve_400() -> None:
    client = TestClient(sandbox_app)
    r = client.get("/ejercicio/no-es-un-hash")
    assert r.status_code == 400


def test_ejercicio_inexistente_devuelve_404(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    client = TestClient(sandbox_app)
    r = client.get(f"/ejercicio/{'a' * 64}")
    assert r.status_code == 404


def test_health() -> None:
    client = TestClient(sandbox_app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "sandbox"

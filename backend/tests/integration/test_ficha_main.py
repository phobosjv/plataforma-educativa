"""Tests del endpoint /ficha/ en la app principal (dev proxy — CLAUDE.md §10).

En dev, pdf_base_url="" y Vite proxea /ficha/ al backend para no requerir el servidor
sandbox separado. En prod, pdf_base_url apunta al sandbox y este endpoint no se llama.
"""

from __future__ import annotations

import hashlib
import os

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app


def _guardar_pdf(media_dir: str, raw: bytes) -> str:
    file_hash = hashlib.sha256(raw).hexdigest()
    destino = os.path.join(media_dir, file_hash[:2])
    os.makedirs(destino, exist_ok=True)
    with open(os.path.join(destino, f"{file_hash}.pdf"), "wb") as f:
        f.write(raw)
    return file_hash


def test_sirve_ficha_pdf_inline(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    raw = b"%PDF-1.7\n...\n%%EOF"
    h = _guardar_pdf(str(tmp_path), raw)

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get(f"/ficha/{h}.pdf")

    assert r.status_code == 200
    assert r.content == raw
    assert r.headers["content-type"] == "application/pdf"
    assert r.headers["content-disposition"] == "inline"
    assert r.headers["access-control-allow-origin"] == "*"


def test_sirve_ficha_pdf_descarga(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    raw = b"%PDF-1.7\n...\n%%EOF"
    h = _guardar_pdf(str(tmp_path), raw)

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get(f"/ficha/{h}.pdf", params={"descargar": 1, "nombre": "mi ficha.pdf"})

    assert r.status_code == 200
    disp = r.headers["content-disposition"]
    assert disp.startswith("attachment;")
    assert "mi ficha" in disp


def test_ficha_main_hash_invalido_devuelve_400() -> None:
    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/ficha/no-es-un-hash.pdf")
    assert r.status_code == 400


def test_ficha_main_inexistente_devuelve_404(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    client = TestClient(app, raise_server_exceptions=False)
    r = client.get(f"/ficha/{'b' * 64}.pdf")
    assert r.status_code == 404

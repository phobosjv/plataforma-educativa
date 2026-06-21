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


def _guardar_pdf(media_dir: str, raw: bytes) -> str:
    file_hash = hashlib.sha256(raw).hexdigest()
    destino = f"{media_dir}/{file_hash[:2]}"
    import os

    os.makedirs(destino, exist_ok=True)
    with open(f"{destino}/{file_hash}.pdf", "wb") as f:
        f.write(raw)
    return file_hash


def test_sirve_ficha_pdf_inline_por_defecto(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    raw = b"%PDF-1.7\n...\n%%EOF"
    h = _guardar_pdf(str(tmp_path), raw)

    client = TestClient(sandbox_app)
    r = client.get(f"/ficha/{h}.pdf")

    assert r.status_code == 200
    assert r.content == raw  # NO se transforma
    assert r.headers["content-type"] == "application/pdf"
    assert r.headers["content-disposition"] == "inline"
    csp = r.headers["content-security-policy"]
    assert "default-src 'none'" in csp and "frame-ancestors" in csp
    assert r.headers["x-content-type-options"] == "nosniff"


def test_ficha_pdf_descarga_attachment_con_nombre_seguro(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    raw = b"%PDF-1.7\n...\n%%EOF"
    h = _guardar_pdf(str(tmp_path), raw)

    client = TestClient(sandbox_app)
    # Nombre con caracteres peligrosos: el sandbox los filtra (anti-inyección de cabecera).
    r = client.get(f"/ficha/{h}.pdf", params={"descargar": 1, "nombre": 'a"\r\nb.pdf'})

    assert r.status_code == 200
    disp = r.headers["content-disposition"]
    assert disp.startswith("attachment;")
    assert '"' not in disp.split("filename=", 1)[1].strip('"')  # comillas internas filtradas
    assert "\r" not in disp and "\n" not in disp


def test_ficha_pdf_hash_invalido_devuelve_400() -> None:
    client = TestClient(sandbox_app)
    r = client.get("/ficha/no-es-un-hash.pdf")
    assert r.status_code == 400


def test_ficha_pdf_inexistente_devuelve_404(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "media_dir", str(tmp_path))
    client = TestClient(sandbox_app)
    r = client.get(f"/ficha/{'a' * 64}.pdf")
    assert r.status_code == 404


def test_health() -> None:
    client = TestClient(sandbox_app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "sandbox"

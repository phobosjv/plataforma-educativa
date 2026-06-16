"""Tests del espejo incremental de la carpeta media."""

from __future__ import annotations

from pathlib import Path

from app.shared.infrastructure.media_backup import MediaMirrorService


def _escribir(base: Path, rel: str, contenido: bytes = b"x") -> None:
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(contenido)


def test_sync_copia_ficheros_nuevos_conservando_estructura(tmp_path: Path) -> None:
    media = tmp_path / "media"
    mirror = tmp_path / "mirror"
    _escribir(media, "images/a.png", b"img")
    _escribir(media, "ejercicios/abc.html", b"<html></html>")

    stats = MediaMirrorService(str(media), str(mirror)).sync()

    assert stats == type(stats)(nuevos=2, total=2)
    assert (mirror / "images/a.png").read_bytes() == b"img"
    assert (mirror / "ejercicios/abc.html").read_bytes() == b"<html></html>"


def test_sync_es_incremental(tmp_path: Path) -> None:
    media = tmp_path / "media"
    mirror = tmp_path / "mirror"
    _escribir(media, "images/a.png")
    servicio = MediaMirrorService(str(media), str(mirror))

    primera = servicio.sync()
    assert primera.nuevos == 1

    # Añadir un fichero nuevo: la segunda pasada solo copia ese.
    _escribir(media, "images/b.png")
    segunda = servicio.sync()
    assert segunda.nuevos == 1
    assert segunda.total == 2

    # Sin cambios: la tercera no copia nada.
    tercera = servicio.sync()
    assert tercera.nuevos == 0
    assert tercera.total == 2


def test_sync_media_inexistente_no_falla(tmp_path: Path) -> None:
    stats = MediaMirrorService(str(tmp_path / "no-existe"), str(tmp_path / "mirror")).sync()
    assert stats.nuevos == 0
    assert stats.total == 0

"""Tests del servicio de exportación completa (BD + media)."""

from __future__ import annotations

import json
import sqlite3
import tarfile
from pathlib import Path

from app.shared.infrastructure.export import ExportService


def _crear_bd(path: Path) -> None:
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT)")
    con.execute("INSERT INTO t (v) VALUES ('hola')")
    con.commit()
    con.close()


def test_export_contiene_bd_media_y_manifest(tmp_path: Path) -> None:
    db = tmp_path / "app.sqlite3"
    _crear_bd(db)
    media = tmp_path / "media"
    (media / "images").mkdir(parents=True)
    (media / "images" / "a.png").write_bytes(b"img")
    (media / "ejercicios").mkdir(parents=True)
    (media / "ejercicios" / "abc.html").write_bytes(b"<html></html>")

    servicio = ExportService(f"sqlite:///{db}", str(media), app_version="9.9.9")
    export_path = servicio.crear(str(tmp_path / "work"))

    assert export_path.exists()
    assert export_path.name.startswith("plataforma-export-")
    assert export_path.name.endswith(".tar.gz")

    with tarfile.open(export_path, "r:gz") as tar:
        nombres = tar.getnames()
        assert "data/app.sqlite3" in nombres
        assert "media/images/a.png" in nombres
        assert "media/ejercicios/abc.html" in nombres
        assert "manifest.json" in nombres

        manifest = json.loads(tar.extractfile("manifest.json").read())  # type: ignore[union-attr]
        assert manifest["app_version"] == "9.9.9"
        assert manifest["num_ficheros_media"] == 2
        assert manifest["formato"] == 1

        # La BD exportada es un SQLite válido con los datos del origen.
        bd_bytes = tar.extractfile("data/app.sqlite3").read()  # type: ignore[union-attr]
        assert bd_bytes[:16] == b"SQLite format 3\x00"


def test_export_sin_media_solo_lleva_bd_y_manifest(tmp_path: Path) -> None:
    db = tmp_path / "app.sqlite3"
    _crear_bd(db)
    servicio = ExportService(f"sqlite:///{db}", str(tmp_path / "media-vacia"), app_version="1.0.0")

    export_path = servicio.crear(str(tmp_path / "work"))

    with tarfile.open(export_path, "r:gz") as tar:
        nombres = tar.getnames()
        assert "data/app.sqlite3" in nombres
        assert "manifest.json" in nombres
        assert not any(n.startswith("media/") for n in nombres)

"""Round-trip de export/import para ficheros content-addressed (fichas PDF y HTML de ejercicio).

Los tests de endpoint solo cubren media bajo ``media/images/``. Las fichas PDF (V-0.22.0) y los
HTML de ejercicio se guardan content-addressed en ``media/<hash[:2]>/<hash>.<ext>`` con el almacén
de producción. Aquí se verifica que esos ficheros sobreviven intactos a Exportar -> Importar, para
blindar contra una regresión que dejase de incluirlos (p. ej. si el export pasara a globar solo
``media/images``).
"""

from __future__ import annotations

import hashlib
import sqlite3
import tarfile
from pathlib import Path

from sqlalchemy import create_engine

from app.contexts.content.infrastructure.html_storage import FileSystemHtmlStorage
from app.contexts.content.infrastructure.pdf_storage import FileSystemPdfStorage
from app.shared.infrastructure.export import ExportService
from app.shared.infrastructure.import_service import ImportService


def _bd_minima(ruta: Path) -> None:
    con = sqlite3.connect(ruta)
    con.execute("CREATE TABLE marca(id INTEGER)")
    con.commit()
    con.close()


def test_round_trip_conserva_ficha_pdf_y_html_content_addressed(tmp_path: Path) -> None:
    src_media = tmp_path / "src_media"
    src_media.mkdir()
    src_db = tmp_path / "src.sqlite3"
    _bd_minima(src_db)

    # Guardar un PDF y un HTML con los almacenes de producción (rutas content-addressed reales).
    raw_pdf = b"%PDF-1.7\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF"
    raw_html = b"<!doctype html><html><body><h1>Ejercicio</h1></body></html>"
    hash_pdf = FileSystemPdfStorage(str(src_media)).save(raw_pdf)
    hash_html = FileSystemHtmlStorage(str(src_media)).save(raw_html)

    rel_pdf = f"{hash_pdf[:2]}/{hash_pdf}.pdf"
    rel_html = f"{hash_html[:2]}/{hash_html}.html"
    assert (src_media / rel_pdf).is_file()
    assert (src_media / rel_html).is_file()

    # Exportar: ambos ficheros deben quedar dentro del .tar.gz.
    export_path = ExportService(f"sqlite:///{src_db}", str(src_media), "0.0.9").crear(
        str(tmp_path / "work")
    )
    with tarfile.open(export_path) as tar:
        nombres = set(tar.getnames())
    assert f"media/{rel_pdf}" in nombres
    assert f"media/{rel_html}" in nombres

    # Importar en un sitio destino "en blanco" (media vacía, BD inexistente).
    dest_media = tmp_path / "dest_media"
    dest_db = tmp_path / "dest.sqlite3"
    backups = tmp_path / "backups"
    backups.mkdir()
    engine = create_engine(f"sqlite:///{dest_db}")
    resultado = ImportService(
        f"sqlite:///{dest_db}", str(dest_media), str(backups), backup_keep=3, engine=engine
    ).importar(export_path)

    # Los ficheros se restauran en su ruta content-addressed y con los bytes intactos
    # (el sha256 del contenido debe seguir coincidiendo con el nombre del fichero).
    pdf_restaurado = dest_media / rel_pdf
    html_restaurado = dest_media / rel_html
    assert pdf_restaurado.is_file()
    assert html_restaurado.is_file()
    assert hashlib.sha256(pdf_restaurado.read_bytes()).hexdigest() == hash_pdf
    assert hashlib.sha256(html_restaurado.read_bytes()).hexdigest() == hash_html
    assert resultado.num_ficheros_media == 2

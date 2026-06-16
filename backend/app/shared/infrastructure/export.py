"""Exportación completa del sitio: BD + media en un único ``.tar.gz`` descargable.

Con el archivo resultante se puede **migrar el servidor** o **recuperar tras un fallo
total**: contiene una copia consistente de la base de datos y la carpeta ``media`` entera,
más un ``manifest.json`` informativo. No incluye el ``.env`` (secretos): se gestiona aparte
en el servidor de destino.

Estructura del archivo:
    data/app.sqlite3      # copia en caliente de la BD (online backup API)
    media/...             # árbol completo de media (ejercicios HTML + imágenes)
    manifest.json         # formato, fecha, versión y conteos
"""

from __future__ import annotations

import io
import json
import logging
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from app.shared.infrastructure.backup import SqliteBackupService

logger = logging.getLogger(__name__)

FORMATO_EXPORT = 1


class ExportService:
    """Construye el archivo de exportación completa (BD + media)."""

    def __init__(self, database_url: str, media_dir: str, app_version: str) -> None:
        self._database_url = database_url
        self._media_dir = Path(media_dir)
        self._app_version = app_version

    def crear(self, work_dir: str) -> Path:
        """Genera el ``.tar.gz`` en ``work_dir`` y devuelve su ruta.

        La BD se copia primero a un fichero temporal con la online backup API (snapshot
        consistente) y luego se añade al tar; así el archivo no captura un WAL a medias.
        """
        work = Path(work_dir)
        work.mkdir(parents=True, exist_ok=True)
        marca = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        export_path = work / f"plataforma-export-{marca}.tar.gz"

        with tempfile.TemporaryDirectory() as tmp:
            db_tmp = Path(tmp) / "app.sqlite3"
            # keep es irrelevante aquí: solo usamos la copia consistente, sin rotación.
            SqliteBackupService(self._database_url, tmp, keep=1).copiar_consistente(db_tmp)

            num_media = 0
            with tarfile.open(export_path, "w:gz") as tar:
                tar.add(db_tmp, arcname="data/app.sqlite3")
                if self._media_dir.exists():
                    for fichero in sorted(self._media_dir.rglob("*")):
                        if fichero.is_file():
                            rel = fichero.relative_to(self._media_dir)
                            tar.add(fichero, arcname=f"media/{rel.as_posix()}")
                            num_media += 1

                manifest = {
                    "formato": FORMATO_EXPORT,
                    "generado_en": datetime.now(timezone.utc).isoformat(),
                    "app_version": self._app_version,
                    "num_ficheros_media": num_media,
                    "tamano_bd_bytes": db_tmp.stat().st_size,
                }
                datos = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
                info = tarfile.TarInfo("manifest.json")
                info.size = len(datos)
                tar.addfile(info, io.BytesIO(datos))

        logger.info(
            "Exportación creada: %s (%d ficheros de media, %d bytes)",
            export_path.name, num_media, export_path.stat().st_size,
        )
        return export_path

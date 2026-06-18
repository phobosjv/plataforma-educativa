"""Importación/restauración completa del sitio desde un ``.tar.gz`` de exportación.

Es la operación inversa de :mod:`app.shared.infrastructure.export`: toma el archivo generado
por «Exportar todo» (BD + media + ``manifest.json``) y deja el sitio destino exactamente con
ese contenido. Sirve para **migrar el servidor** o **restaurar tras un fallo total**.

Es destructivo (reemplaza la BD y restaura la media), por eso el endpoint exige confirmación
explícita y este servicio crea **antes** una copia de seguridad de la BD actual (rollback).

Infra pura: no conoce FastAPI ni el dominio. El intercambio del fichero SQLite se hace de forma
segura: se cierran las conexiones del pool (``engine.dispose()``) y se sustituye el fichero con
un ``os.replace`` atómico (rename), de modo que las conexiones aún abiertas conservan el inodo
antiguo y las nuevas abren ya la BD importada, sin corromper nada.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sqlite3
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.engine import Engine

from app.shared.domain.base import DomainError
from app.shared.infrastructure.backup import SqliteBackupService, _ruta_bd_desde_url
from app.shared.infrastructure.export import FORMATO_EXPORT

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImportResult:
    """Resumen de una importación realizada con éxito."""

    num_ficheros_media: int
    app_version_origen: str
    backup_seguridad: str | None


class ImportService:
    """Restaura el sitio (BD + media) a partir de un archivo de exportación."""

    def __init__(
        self,
        database_url: str,
        media_dir: str,
        backup_dir: str,
        backup_keep: int,
        engine: Engine,
    ) -> None:
        self._database_url = database_url
        self._db_path = _ruta_bd_desde_url(database_url)
        self._media_dir = Path(media_dir)
        self._backup_dir = backup_dir
        self._backup_keep = backup_keep
        self._engine = engine

    def importar(self, archivo: Path) -> ImportResult:
        """Valida el archivo y restaura la BD y la media del sitio. Operación destructiva.

        Pasos: (1) extraer de forma segura, (2) validar manifest y la integridad de la BD,
        (3) copia de seguridad de la BD actual, (4) cerrar conexiones, (5) restaurar media,
        (6) intercambiar el fichero de BD de forma atómica.
        """
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            self._extraer_seguro(archivo, tmp)

            manifest = self._leer_manifest(tmp)
            db_extraida = tmp / "data" / "app.sqlite3"
            if not db_extraida.is_file():
                raise DomainError("El archivo no contiene la base de datos (data/app.sqlite3).")
            self._validar_sqlite(db_extraida)

            # (3) Copia de seguridad de la BD actual ANTES de sobrescribir (rollback posible).
            backup_nombre: str | None = None
            if self._db_path.exists():
                info = SqliteBackupService(
                    self._database_url, self._backup_dir, self._backup_keep
                ).crear_backup()
                backup_nombre = info.nombre

            # (4) Cerrar todas las conexiones del pool a la BD vieja antes del intercambio.
            self._engine.dispose()

            # (5) Restaurar media (mezcla: copia los ficheros del archivo, son inmutables).
            num_media = self._restaurar_media(tmp / "media")

            # (6) Intercambio atómico del fichero de BD + limpieza de WAL/SHM obsoletos.
            self._intercambiar_bd(db_extraida)

        logger.info(
            "Importación completada: %d ficheros de media, BD de la versión %s (backup previo: %s)",
            num_media, manifest.get("app_version", "?"), backup_nombre,
        )
        return ImportResult(
            num_ficheros_media=num_media,
            app_version_origen=str(manifest.get("app_version", "")),
            backup_seguridad=backup_nombre,
        )

    # ── Pasos internos ──────────────────────────────────────────────────────────

    def _extraer_seguro(self, archivo: Path, destino: Path) -> None:
        """Extrae solo ``data/``, ``media/`` y ``manifest.json``, sin permitir path traversal."""
        try:
            tar = tarfile.open(archivo, "r:gz")
        except (tarfile.TarError, OSError) as e:
            raise DomainError("El archivo no es una exportación válida (.tar.gz).") from e
        with tar:
            raiz_destino = destino.resolve()
            for miembro in tar.getmembers():
                # Solo ficheros y directorios normales (nunca enlaces ni dispositivos).
                if not (miembro.isfile() or miembro.isdir()):
                    continue
                nombre = miembro.name.lstrip("/")
                partes = Path(nombre).parts
                if not partes or ".." in partes or Path(nombre).is_absolute():
                    raise DomainError("Archivo de importación inválido (ruta no permitida).")
                if partes[0] not in ("data", "media") and nombre != "manifest.json":
                    continue  # se ignora cualquier entrada inesperada
                objetivo = (destino / nombre).resolve()
                if raiz_destino not in objetivo.parents and objetivo != raiz_destino:
                    raise DomainError("Archivo de importación inválido (ruta fuera de destino).")
                if miembro.isdir():
                    objetivo.mkdir(parents=True, exist_ok=True)
                    continue
                objetivo.parent.mkdir(parents=True, exist_ok=True)
                extraido = tar.extractfile(miembro)
                if extraido is None:
                    continue
                with extraido as src, open(objetivo, "wb") as out:
                    shutil.copyfileobj(src, out)

    def _leer_manifest(self, tmp: Path) -> dict:
        ruta = tmp / "manifest.json"
        if not ruta.is_file():
            raise DomainError("El archivo no contiene manifest.json: no es una exportación válida.")
        try:
            manifest = json.loads(ruta.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise DomainError("El manifest.json del archivo está dañado.") from e
        if manifest.get("formato") != FORMATO_EXPORT:
            raise DomainError(
                f"Formato de exportación no soportado (se esperaba {FORMATO_EXPORT}, "
                f"llegó {manifest.get('formato')!r})."
            )
        return manifest

    def _validar_sqlite(self, db_path: Path) -> None:
        """Comprueba que el fichero es una BD SQLite íntegra (no un archivo arbitrario)."""
        try:
            con = sqlite3.connect(db_path)
            try:
                fila = con.execute("PRAGMA integrity_check").fetchone()
            finally:
                con.close()
        except sqlite3.DatabaseError as e:
            raise DomainError("La base de datos del archivo no es válida o está dañada.") from e
        if not fila or fila[0] != "ok":
            raise DomainError("La base de datos del archivo está dañada (integrity_check).")

    def _restaurar_media(self, origen: Path) -> int:
        if not origen.exists():
            return 0
        num = 0
        for fichero in origen.rglob("*"):
            if not fichero.is_file():
                continue
            destino = self._media_dir / fichero.relative_to(origen)
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(fichero, destino)
            num += 1
        return num

    def _intercambiar_bd(self, db_nueva: Path) -> None:
        """Sustituye el fichero de BD por el importado con un ``os.replace`` atómico."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        provisional = self._db_path.with_name(self._db_path.name + ".importing")
        shutil.copy2(db_nueva, provisional)
        os.replace(provisional, self._db_path)  # atómico en el mismo sistema de ficheros
        # El WAL/SHM antiguos ya no corresponden a la BD nueva (la copia es un fichero único
        # y consistente); se eliminan para no mezclar estados.
        for sufijo in ("-wal", "-shm"):
            obsoleto = self._db_path.with_name(self._db_path.name + sufijo)
            if obsoleto.exists():
                try:
                    obsoleto.unlink()
                except OSError:
                    logger.warning("No se pudo eliminar %s tras la importación.", obsoleto.name)

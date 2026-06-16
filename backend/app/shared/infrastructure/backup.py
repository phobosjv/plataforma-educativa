"""Copias de seguridad en caliente de la base de datos SQLite.

Usa la *online backup API* de ``sqlite3`` (``Connection.backup``), que produce una copia
consistente sin bloquear la BD ni corromperse con el modo WAL (a diferencia de un simple
``copy`` del fichero, que puede capturar un WAL a medias). Cada copia es un fichero
``.sqlite3`` autónomo; se rotan conservando solo las más recientes.

Infra pura: no conoce FastAPI ni el dominio. El path de la BD se deriva de ``database_url``.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

_SQLITE_PREFIX = "sqlite:///"


@dataclass(frozen=True)
class BackupInfo:
    """Metadatos de un fichero de copia de seguridad existente."""

    nombre: str
    tamano_bytes: int
    creado_en: datetime


def _ruta_bd_desde_url(database_url: str) -> Path:
    """Extrae la ruta del fichero SQLite de una ``database_url`` de SQLAlchemy."""
    if not database_url.startswith(_SQLITE_PREFIX):
        raise ValueError(f"Solo se admiten copias de SQLite, no de: {database_url!r}")
    return Path(database_url[len(_SQLITE_PREFIX) :])


class SqliteBackupService:
    """Crea, lista y rota copias de seguridad del fichero SQLite de la aplicación."""

    def __init__(self, database_url: str, backup_dir: str, keep: int) -> None:
        self._db_path = _ruta_bd_desde_url(database_url)
        self._backup_dir = Path(backup_dir)
        self._keep = max(1, keep)

    def crear_backup(self) -> BackupInfo:
        """Genera una copia consistente y rota las antiguas. Devuelve la copia creada."""
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        marca = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        destino = self._backup_dir / f"app-{marca}.sqlite3"

        # connect en modo solo-lectura del origen no es imprescindible: backup() toma un
        # snapshot consistente aunque haya escrituras concurrentes.
        origen = sqlite3.connect(self._db_path)
        try:
            copia = sqlite3.connect(destino)
            try:
                origen.backup(copia)
            finally:
                copia.close()
        finally:
            origen.close()

        self._rotar()
        info = self._info(destino)
        logger.info("Backup creado: %s (%d bytes)", info.nombre, info.tamano_bytes)
        return info

    def listar_backups(self) -> list[BackupInfo]:
        """Lista las copias existentes, de la más reciente a la más antigua."""
        if not self._backup_dir.exists():
            return []
        copias = [self._info(p) for p in self._backup_dir.glob("app-*.sqlite3")]
        return sorted(copias, key=lambda b: b.nombre, reverse=True)

    def _rotar(self) -> None:
        """Elimina las copias más antiguas dejando solo las ``keep`` más recientes.

        El orden por nombre coincide con el cronológico porque la marca de tiempo va en
        el nombre con formato fijo ``YYYYMMDD-HHMMSS``.
        """
        copias = sorted(self._backup_dir.glob("app-*.sqlite3"), key=lambda p: p.name)
        sobrantes = copias[: -self._keep] if len(copias) > self._keep else []
        for p in sobrantes:
            try:
                p.unlink()
                logger.info("Backup antiguo eliminado por rotación: %s", p.name)
            except OSError:
                logger.warning("No se pudo eliminar el backup antiguo: %s", p.name)

    @staticmethod
    def _info(path: Path) -> BackupInfo:
        st = path.stat()
        return BackupInfo(
            nombre=path.name,
            tamano_bytes=st.st_size,
            creado_en=datetime.fromtimestamp(st.st_mtime, tz=timezone.utc),
        )

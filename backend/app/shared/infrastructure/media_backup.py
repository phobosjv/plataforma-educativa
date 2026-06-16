"""Copia incremental de la carpeta ``media`` (ejercicios HTML + imágenes).

Los ficheros de ``media`` son **content-addressed** (su nombre deriva del hash del
contenido): una vez escritos, son inmutables y nunca cambian, solo se añaden nuevos. Eso
hace que un espejo incremental sea trivial y barato: basta copiar los ficheros que aún no
estén en el espejo; los ya copiados nunca hay que rehacerlos.

Infra pura: no conoce FastAPI ni el dominio.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MirrorStats:
    """Resultado de una sincronización del espejo de media."""

    nuevos: int  # ficheros copiados en esta pasada
    total: int  # ficheros presentes en el origen


class MediaMirrorService:
    """Mantiene un espejo incremental de ``media`` en otro directorio."""

    def __init__(self, media_dir: str, mirror_dir: str) -> None:
        self._media_dir = Path(media_dir)
        self._mirror_dir = Path(mirror_dir)

    def sync(self) -> MirrorStats:
        """Copia al espejo los ficheros que aún no estén. Devuelve las estadísticas.

        Solo añade: como el contenido es inmutable, un fichero ya presente en el espejo
        es idéntico al del origen y no se vuelve a copiar.
        """
        if not self._media_dir.exists():
            return MirrorStats(nuevos=0, total=0)

        nuevos = 0
        total = 0
        for origen in self._media_dir.rglob("*"):
            if not origen.is_file():
                continue
            total += 1
            rel = origen.relative_to(self._media_dir)
            destino = self._mirror_dir / rel
            if destino.exists():
                continue
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen, destino)
            nuevos += 1

        if nuevos:
            logger.info("Espejo de media: %d fichero(s) nuevos (%d en total).", nuevos, total)
        return MirrorStats(nuevos=nuevos, total=total)

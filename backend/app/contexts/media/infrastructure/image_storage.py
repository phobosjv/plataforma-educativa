"""Almacén de imágenes de artículos, direccionado por contenido (SHA-256, inmutable).

Las imágenes (raster) son contenido seguro y se sirven desde el ORIGEN de la app
(a diferencia de los ejercicios interactivos, que van aislados en el sandbox).
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


class FileSystemImageStorage:
    def __init__(self, base_dir: str) -> None:
        # Subcarpeta dedicada para no mezclarse con los HTML de ejercicios.
        self._base = Path(base_dir) / "images"

    def save(self, raw: bytes, ext: str) -> str:
        """Guarda la imagen y devuelve su URL relativa al origen de la app."""
        file_hash = hashlib.sha256(raw).hexdigest()
        nombre = f"{file_hash}.{ext}"
        target = self._base / nombre
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_path = tempfile.mkstemp(dir=target.parent)
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(raw)
                os.replace(tmp_path, target)
            except Exception:
                os.unlink(tmp_path)
                raise
        return f"/media/images/{nombre}"

"""Almacén de ficheros HTML direccionado por contenido (SHA-256, inmutable)."""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


class FileSystemHtmlStorage:
    def __init__(self, base_dir: str) -> None:
        self._base = Path(base_dir)

    def save(self, raw_html: bytes) -> str:
        file_hash = hashlib.sha256(raw_html).hexdigest()
        target = self._base / file_hash[:2] / f"{file_hash}.html"
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            # Escritura atómica: temp → rename
            fd, tmp_path = tempfile.mkstemp(dir=target.parent)
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(raw_html)
                # mkstemp crea el fichero con 0o600 (solo el dueño). El sandbox lo sirve
                # como otro usuario (nginx) -> daría 403. El HTML de ejercicio es contenido
                # público servido aislado, así que se hace legible por todos (0o644).
                os.chmod(tmp_path, 0o644)
                os.replace(tmp_path, target)
            except Exception:
                os.unlink(tmp_path)
                raise
        return file_hash

    def url_for(self, file_hash: str) -> str:
        # Ruta canónica del ejercicio, relativa al origen sandbox. El servidor sandbox
        # (app.sandbox / nginx/sandbox.conf) la resuelve al fichero content-addressed.
        return f"/ejercicio/{file_hash}"

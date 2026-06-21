"""Almacén de ficheros PDF direccionado por contenido (SHA-256, inmutable).

Espejo de ``FileSystemHtmlStorage`` para las fichas PDF. Los ficheros viven junto a los
HTML de ejercicios en ``media/<hash[:2]>/<hash>.pdf`` y se sirven aislados desde el origen
sandbox (``app/sandbox.py`` en dev, ``nginx/sandbox.conf`` en prod).
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path


class FileSystemPdfStorage:
    def __init__(self, base_dir: str) -> None:
        self._base = Path(base_dir)

    def save(self, raw_pdf: bytes) -> str:
        file_hash = hashlib.sha256(raw_pdf).hexdigest()
        target = self._base / file_hash[:2] / f"{file_hash}.pdf"
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            # Escritura atómica: temp → rename
            fd, tmp_path = tempfile.mkstemp(dir=target.parent)
            try:
                with os.fdopen(fd, "wb") as f:
                    f.write(raw_pdf)
                # mkstemp crea el fichero con 0o600 (solo el dueño). El sandbox lo sirve como
                # otro usuario (nginx) -> daría 403. La ficha PDF es contenido público servido
                # aislado, así que se hace legible por todos (0o644), igual que el HTML.
                os.chmod(tmp_path, 0o644)
                os.replace(tmp_path, target)
            except Exception:
                os.unlink(tmp_path)
                raise
        return file_hash

    def url_for(self, file_hash: str) -> str:
        # Ruta canónica de la ficha, relativa al origen sandbox. El servidor sandbox
        # (app.sandbox / nginx/sandbox.conf) la resuelve al fichero content-addressed.
        return f"/ficha/{file_hash}.pdf"

"""Script: crea dist/plataforma-educativa-v{VERSION}.zip."""

import os
import zipfile

VERSION = "v0.8.3"
SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(SRC, "dist")
ZIP_NAME = f"plataforma-educativa-{VERSION}.zip"
ZIP_PATH = os.path.join(DIST_DIR, ZIP_NAME)
PREFIX = f"plataforma-educativa-{VERSION}/"

# Directorios a excluir en CUALQUIER nivel (artefactos).
EXCLUDE_DIRS = {
    "__pycache__", ".git", ".venv", "venv", "node_modules",
    "dist", ".mypy_cache", ".ruff_cache", ".pytest_cache", ".eggs",
}
# Directorios RUNTIME a excluir SOLO en la raíz del repo o de backend/ (no el código
# fuente backend/app/contexts/media/, que es un contexto del dominio).
EXCLUDE_DIRS_ANCLADOS = {"data", "media"}
RAICES_RUNTIME = {"", "backend"}
EXCLUDE_EXTS = {".pyc", ".pyo", ".sqlite3", ".sqlite", ".db"}
EXCLUDE_FILES = {".env"}


def should_exclude(rel_path: str) -> bool:
    parts = rel_path.replace("\\", "/").split("/")
    for part in parts[:-1]:
        if part in EXCLUDE_DIRS:
            return True
    # data/ y media/ solo se excluyen si cuelgan de la raíz o de backend/.
    for i, part in enumerate(parts[:-1]):
        if part in EXCLUDE_DIRS_ANCLADOS and "/".join(parts[:i]) in RAICES_RUNTIME:
            return True
    filename = parts[-1]
    if filename in EXCLUDE_FILES:
        return True
    _, ext = os.path.splitext(filename)
    if ext in EXCLUDE_EXTS:
        return True
    return False


os.makedirs(DIST_DIR, exist_ok=True)

count = 0
with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
    for dirpath, dirnames, filenames in os.walk(SRC):
        rel_dir = os.path.relpath(dirpath, SRC)
        if rel_dir == ".":
            rel_dir = ""
        rel_dir_norm = rel_dir.replace("\\", "/")
        # Prune artefactos en cualquier nivel; data/media solo en raíz o backend/.
        dirnames[:] = [
            d
            for d in dirnames
            if d not in EXCLUDE_DIRS
            and not (d in EXCLUDE_DIRS_ANCLADOS and rel_dir_norm in RAICES_RUNTIME)
        ]
        for filename in filenames:
            rel_file = os.path.join(rel_dir, filename) if rel_dir else filename
            if should_exclude(rel_file):
                continue
            abs_path = os.path.join(dirpath, filename)
            arcname = PREFIX + rel_file.replace("\\", "/")
            zf.write(abs_path, arcname)
            count += 1

size_kb = os.path.getsize(ZIP_PATH) // 1024
print(f"Creado: {ZIP_PATH}")
print(f"  {count} ficheros, {size_kb} KB")

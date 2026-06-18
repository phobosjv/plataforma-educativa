"""Endpoints de mantenimiento operativo (solo admin): copias de seguridad de la BD.

La purga de la papelera es automática (tarea en segundo plano) y no se expone aquí. Estas
rutas permiten al admin ver las copias existentes y lanzar una copia manual bajo demanda.
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from starlette.background import BackgroundTask

from app.config import settings
from app.contexts.analytics.infrastructure.buffer import buffer_visitas
from app.contexts.identity.api.dependencies import require_admin
from app.contexts.identity.application.dtos import UsuarioDTO
from app.shared.domain.base import DomainError
from app.shared.infrastructure.backup import BackupInfo, SqliteBackupService
from app.shared.infrastructure.database import engine
from app.shared.infrastructure.export import ExportService
from app.shared.infrastructure.import_service import ImportService
from app.version import __version__

router = APIRouter(tags=["maintenance"])

# Texto que el admin debe escribir para confirmar una importación (operación destructiva).
CONFIRMACION_IMPORT = "IMPORTAR"


def _migrar_bd_a_head() -> None:
    """Lleva la BD recién importada al esquema actual (``alembic upgrade head``).

    Así una exportación de una versión anterior queda **migrada** al esquema de esta versión.
    Si ya está al día, es una operación sin efecto. Se resuelven las rutas de Alembic respecto
    a la raíz de ``backend/`` para no depender del directorio de trabajo.
    """
    raiz = Path(__file__).resolve().parents[3]  # backend/
    cfg = Config(str(raiz / "alembic.ini"))
    cfg.set_main_option("script_location", str(raiz / "migrations"))
    command.upgrade(cfg, "head")


class BackupResponse(BaseModel):
    nombre: str
    tamano_bytes: int
    creado_en: datetime


def _to_response(info: BackupInfo) -> BackupResponse:
    return BackupResponse(
        nombre=info.nombre, tamano_bytes=info.tamano_bytes, creado_en=info.creado_en
    )


def _servicio() -> SqliteBackupService:
    return SqliteBackupService(
        settings.database_url, settings.backup_dir, settings.backup_keep
    )


@router.get("/admin/backups", response_model=list[BackupResponse])
def listar_backups(_: UsuarioDTO = Depends(require_admin)) -> list[BackupResponse]:
    """Lista las copias de seguridad existentes (de la más reciente a la más antigua)."""
    return [_to_response(b) for b in _servicio().listar_backups()]


@router.post(
    "/admin/backups", response_model=BackupResponse, status_code=status.HTTP_201_CREATED
)
def crear_backup(_: UsuarioDTO = Depends(require_admin)) -> BackupResponse:
    """Genera una copia de seguridad de la BD de inmediato y rota las antiguas."""
    return _to_response(_servicio().crear_backup())


@router.get("/admin/backups/{nombre}")
def descargar_backup(nombre: str, _: UsuarioDTO = Depends(require_admin)) -> FileResponse:
    """Descarga el fichero de una copia de seguridad (solo admin).

    El nombre se valida en el servicio (formato exacto + contención en el directorio de
    copias) para impedir cualquier path traversal. Se sirve como adjunto para que el
    navegador lo descargue al PC del administrador.
    """
    ruta = _servicio().ruta_de(nombre)
    if ruta is None:
        raise HTTPException(status_code=404, detail="Copia de seguridad no encontrada.")
    return FileResponse(ruta, media_type="application/octet-stream", filename=nombre)


def _borrar_temporal(ruta: Path) -> None:
    try:
        os.unlink(ruta)
    except OSError:
        pass


@router.post("/admin/export")
def exportar_todo(_: UsuarioDTO = Depends(require_admin)) -> FileResponse:
    """Genera y descarga la exportación completa (BD + media) como ``.tar.gz`` (solo admin).

    Con este archivo se puede migrar el servidor o recuperar el sitio entero. Se construye
    en un temporal bajo el directorio de backups y se elimina después de enviarlo.
    """
    work = str(Path(settings.backup_dir) / "tmp")
    export_path = ExportService(settings.database_url, settings.media_dir, __version__).crear(work)
    return FileResponse(
        export_path,
        media_type="application/gzip",
        filename=export_path.name,
        background=BackgroundTask(_borrar_temporal, export_path),
    )


class ImportResponse(BaseModel):
    ok: bool
    num_ficheros_media: int
    app_version_importada: str
    backup_seguridad: str | None
    detalle: str


@router.post("/admin/import", response_model=ImportResponse)
async def importar_todo(
    fichero: UploadFile = File(...),
    confirmacion: str = Form(...),
    _: UsuarioDTO = Depends(require_admin),
) -> ImportResponse:
    """Restaura el sitio (BD + media) desde una exportación ``.tar.gz`` (solo admin).

    Operación **destructiva**: reemplaza la base de datos y restaura la media. Exige escribir
    ``IMPORTAR`` en ``confirmacion`` y crea automáticamente una copia de seguridad de la BD
    actual antes de sobrescribir. Tras importar, la BD se migra al esquema actual. La sesión
    del administrador puede dejar de ser válida (el usuario procede de la BD importada).
    """
    if confirmacion.strip() != CONFIRMACION_IMPORT:
        raise HTTPException(
            status_code=400,
            detail=f"Confirmación incorrecta: escribe '{CONFIRMACION_IMPORT}' para importar.",
        )

    work = Path(settings.backup_dir) / "tmp"
    work.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(delete=False, dir=work, suffix=".tar.gz")
    tmp_path = Path(tmp.name)
    try:
        while True:
            chunk = await fichero.read(1024 * 1024)
            if not chunk:
                break
            tmp.write(chunk)
        tmp.close()

        service = ImportService(
            settings.database_url,
            settings.media_dir,
            settings.backup_dir,
            settings.backup_keep,
            engine,
        )
        result = service.importar(tmp_path)
        _migrar_bd_a_head()
        # Descartar las visitas en memoria del sitio ANTERIOR: sus IDs de contenido no
        # corresponden a la BD recién importada (si no, se volcarían como filas huérfanas).
        buffer_visitas.drenar()
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if not tmp.closed:
            tmp.close()
        _borrar_temporal(tmp_path)

    return ImportResponse(
        ok=True,
        num_ficheros_media=result.num_ficheros_media,
        app_version_importada=result.app_version_origen,
        backup_seguridad=result.backup_seguridad,
        detalle="Sitio restaurado. Vuelve a iniciar sesión con las credenciales del sitio importado.",
    )

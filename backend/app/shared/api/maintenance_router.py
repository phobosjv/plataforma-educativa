"""Endpoints de mantenimiento operativo (solo admin): copias de seguridad de la BD.

La purga de la papelera es automática (tarea en segundo plano) y no se expone aquí. Estas
rutas permiten al admin ver las copias existentes y lanzar una copia manual bajo demanda.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import settings
from app.contexts.identity.api.dependencies import require_admin
from app.contexts.identity.application.dtos import UsuarioDTO
from app.shared.infrastructure.backup import BackupInfo, SqliteBackupService

router = APIRouter(tags=["maintenance"])


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

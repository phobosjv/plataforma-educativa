"""Router del contexto MEDIA: subida de imágenes de artículos."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import settings
from app.contexts.media.application.handlers import GuardarImagenHandler
from app.contexts.media.infrastructure.image_storage import FileSystemImageStorage
from app.contexts.identity.api.dependencies import require_editor_or_admin
from app.contexts.identity.application.dtos import UsuarioDTO
from app.shared.domain.base import DomainError

router = APIRouter(prefix="/media", tags=["media"])


class ImagenSubidaResponse(BaseModel):
    url: str


@router.post("/imagenes", response_model=ImagenSubidaResponse)
def subir_imagen(
    fichero: UploadFile = File(...),
    _: UsuarioDTO = Depends(require_editor_or_admin),
) -> ImagenSubidaResponse:
    raw = fichero.file.read()
    storage = FileSystemImageStorage(settings.media_dir)
    handler = GuardarImagenHandler(storage)
    try:
        url = handler.handle(raw, fichero.content_type)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ImagenSubidaResponse(url=url)

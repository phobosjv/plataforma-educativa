"""Dependencies FastAPI para autenticación y autorización por rol."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.contexts.identity.application.dtos import UsuarioDTO, usuario_to_dto
from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
from app.config import settings
from app.shared.domain.base import AuthenticationError
from app.shared.infrastructure.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def get_current_usuario(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UsuarioDTO:
    auth = ArgonAuthService(settings.secret_key, settings.access_token_expire_minutes)
    repo = SqlAlchemyUsuarioRepository(db)

    try:
        data = auth.decode_token(token)
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    usuario_id_str = data.get("sub")
    if not usuario_id_str:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin sujeto.")

    try:
        uid = UUID(usuario_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token malformado.")

    usuario = repo.get_by_id(uid)
    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
        )

    return usuario_to_dto(usuario)


def require_admin(current: UsuarioDTO = Depends(get_current_usuario)) -> UsuarioDTO:
    if current.rol != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Se requiere rol admin.")
    return current


def require_editor_or_admin(current: UsuarioDTO = Depends(get_current_usuario)) -> UsuarioDTO:
    if current.rol not in {"admin", "editor"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol editor o admin.",
        )
    return current

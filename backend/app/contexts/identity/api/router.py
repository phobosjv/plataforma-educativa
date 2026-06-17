"""Router del contexto IDENTITY: autenticación y gestión de usuarios."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.contexts.identity.api.dependencies import require_admin
from app.contexts.identity.api.schemas import CrearUsuarioRequest, TokenResponse, UsuarioResponse
from app.contexts.identity.application.commands import CrearUsuarioCommand, LoginCommand
from app.contexts.identity.application.dtos import UsuarioDTO
from app.contexts.identity.application.handlers import (
    CrearUsuarioHandler,
    ListarUsuariosHandler,
    LoginHandler,
)
from app.contexts.identity.application.queries import ListarUsuariosQuery
from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.contexts.identity.infrastructure.repositories import SqlAlchemyUsuarioRepository
from app.config import settings
from app.contexts.auditing.infrastructure.recorder import registrar_auditoria
from app.shared.domain.base import AuthenticationError, DomainError
from app.shared.infrastructure.database import get_db
from app.shared.infrastructure.unit_of_work import UnitOfWork

router = APIRouter(tags=["identity"])


def _make_login_handler(db: Session) -> LoginHandler:
    repo = SqlAlchemyUsuarioRepository(db)
    auth = ArgonAuthService(settings.secret_key, settings.access_token_expire_minutes)
    uow = UnitOfWork(db)
    return LoginHandler(repo, auth, uow)


def _make_crear_usuario_handler(db: Session) -> CrearUsuarioHandler:
    repo = SqlAlchemyUsuarioRepository(db)
    auth = ArgonAuthService(settings.secret_key, settings.access_token_expire_minutes)
    uow = UnitOfWork(db)
    return CrearUsuarioHandler(repo, auth, uow)


def _make_listar_handler(db: Session) -> ListarUsuariosHandler:
    repo = SqlAlchemyUsuarioRepository(db)
    return ListarUsuariosHandler(repo)


@router.post("/auth/token", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    handler = _make_login_handler(db)
    try:
        token = handler.handle(LoginCommand(email=form.username, password=form.password))
    except AuthenticationError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=token)


@router.get("/users/", response_model=list[UsuarioResponse])
def listar_usuarios(
    _: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[UsuarioResponse]:
    handler = _make_listar_handler(db)
    dtos = handler.handle(ListarUsuariosQuery())
    return [
        UsuarioResponse(id=d.id, email=d.email, rol=d.rol, activo=d.activo, created_at=d.created_at)
        for d in dtos
    ]


@router.post("/users/", status_code=status.HTTP_201_CREATED)
def crear_usuario(
    body: CrearUsuarioRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    handler = _make_crear_usuario_handler(db)
    try:
        uid = handler.handle(
            CrearUsuarioCommand(email=body.email, password=body.password, rol=body.rol)
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    registrar_auditoria(
        db, usuario_id=current.id, usuario_email=current.email, usuario_rol=current.rol,
        accion="crear", entidad="usuario", entidad_id=str(uid), detalle=body.email,
    )
    return {"id": str(uid)}

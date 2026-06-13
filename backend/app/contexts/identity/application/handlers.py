"""Handlers de comandos y queries del contexto IDENTITY."""

from __future__ import annotations

from uuid import UUID

from app.contexts.identity.application.commands import CrearUsuarioCommand, LoginCommand
from app.contexts.identity.application.dtos import UsuarioDTO, usuario_to_dto
from app.contexts.identity.application.queries import ListarUsuariosQuery, ObtenerUsuarioPorIdQuery
from app.contexts.identity.domain.model import Rol, Usuario
from app.contexts.identity.domain.ports import UsuarioRepository
from app.contexts.identity.domain.services import AuthService
from app.shared.domain.base import AuthenticationError, DomainError, NotFoundError
from app.shared.infrastructure.unit_of_work import UnitOfWork


class LoginHandler:
    def __init__(self, repo: UsuarioRepository, auth: AuthService, uow: UnitOfWork) -> None:
        self._repo = repo
        self._auth = auth
        self._uow = uow

    def handle(self, cmd: LoginCommand) -> str:
        usuario = self._repo.get_by_email(cmd.email)
        if usuario is None:
            raise AuthenticationError("Credenciales inválidas.")
        if not self._auth.verify_password(cmd.password, usuario.hashed_password):
            raise AuthenticationError("Credenciales inválidas.")
        if not usuario.activo:
            raise AuthenticationError("Usuario inactivo.")
        return self._auth.create_access_token(str(usuario.id), usuario.rol.value)


class CrearUsuarioHandler:
    def __init__(self, repo: UsuarioRepository, auth: AuthService, uow: UnitOfWork) -> None:
        self._repo = repo
        self._auth = auth
        self._uow = uow

    def handle(self, cmd: CrearUsuarioCommand) -> UUID:
        if self._repo.get_by_email(cmd.email) is not None:
            raise DomainError("El email ya está registrado.")
        try:
            rol = Rol(cmd.rol)
        except ValueError:
            raise DomainError(f"Rol inválido: '{cmd.rol}'. Use 'admin' o 'editor'.")
        hashed = self._auth.hash_password(cmd.password)
        usuario = Usuario.crear(cmd.email, hashed, rol)
        self._repo.add(usuario)
        self._uow.commit()
        return usuario.id


class ListarUsuariosHandler:
    def __init__(self, repo: UsuarioRepository) -> None:
        self._repo = repo

    def handle(self, query: ListarUsuariosQuery) -> list[UsuarioDTO]:
        return [usuario_to_dto(u) for u in self._repo.list_all()]


class ObtenerUsuarioPorIdHandler:
    def __init__(self, repo: UsuarioRepository) -> None:
        self._repo = repo

    def handle(self, query: ObtenerUsuarioPorIdQuery) -> UsuarioDTO:
        usuario = self._repo.get_by_id(query.usuario_id)
        if usuario is None:
            raise NotFoundError(f"Usuario {query.usuario_id} no encontrado.")
        return usuario_to_dto(usuario)

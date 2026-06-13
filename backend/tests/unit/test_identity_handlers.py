"""Tests unitarios de los handlers de identity (con mocks, sin I/O)."""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.contexts.identity.application.commands import CrearUsuarioCommand, LoginCommand
from app.contexts.identity.application.handlers import CrearUsuarioHandler, LoginHandler
from app.contexts.identity.application.queries import ListarUsuariosQuery
from app.contexts.identity.application.handlers import ListarUsuariosHandler
from app.contexts.identity.domain.model import Rol, Usuario
from app.shared.domain.base import AuthenticationError, DomainError


def _make_usuario(email: str = "u@test.es", activo: bool = True) -> Usuario:
    return Usuario(
        id=uuid4(),
        email=email,
        hashed_password="hash",
        rol=Rol.EDITOR,
        activo=activo,
    )


def _make_login_handler(
    usuario: Usuario | None,
    verify_result: bool = True,
) -> LoginHandler:
    repo = MagicMock()
    repo.get_by_email.return_value = usuario
    auth = MagicMock()
    auth.verify_password.return_value = verify_result
    auth.create_access_token.return_value = "token_jwt"
    uow = MagicMock()
    return LoginHandler(repo, auth, uow)


class TestLoginHandler:
    def test_credenciales_correctas_devuelve_token(self) -> None:
        u = _make_usuario()
        handler = _make_login_handler(u, verify_result=True)
        token = handler.handle(LoginCommand("u@test.es", "pass"))
        assert token == "token_jwt"

    def test_usuario_no_encontrado_lanza_error(self) -> None:
        handler = _make_login_handler(None)
        with pytest.raises(AuthenticationError):
            handler.handle(LoginCommand("nadie@test.es", "pass"))

    def test_password_incorrecta_lanza_error(self) -> None:
        u = _make_usuario()
        handler = _make_login_handler(u, verify_result=False)
        with pytest.raises(AuthenticationError):
            handler.handle(LoginCommand("u@test.es", "mala"))

    def test_usuario_inactivo_lanza_error(self) -> None:
        u = _make_usuario(activo=False)
        handler = _make_login_handler(u, verify_result=True)
        with pytest.raises(AuthenticationError):
            handler.handle(LoginCommand("u@test.es", "pass"))


class TestCrearUsuarioHandler:
    def _make_handler(self, email_existe: bool = False) -> CrearUsuarioHandler:
        repo = MagicMock()
        repo.get_by_email.return_value = _make_usuario() if email_existe else None
        auth = MagicMock()
        auth.hash_password.return_value = "hash_argon"
        uow = MagicMock()
        return CrearUsuarioHandler(repo, auth, uow)

    def test_crear_exitoso_devuelve_uuid(self) -> None:
        handler = self._make_handler(email_existe=False)
        uid = handler.handle(CrearUsuarioCommand("nuevo@test.es", "password1", "editor"))
        assert uid is not None

    def test_email_duplicado_lanza_error(self) -> None:
        handler = self._make_handler(email_existe=True)
        with pytest.raises(DomainError):
            handler.handle(CrearUsuarioCommand("existe@test.es", "password1", "editor"))

    def test_rol_invalido_lanza_error(self) -> None:
        handler = self._make_handler(email_existe=False)
        with pytest.raises(DomainError):
            handler.handle(CrearUsuarioCommand("nuevo@test.es", "password1", "superadmin"))


class TestListarUsuariosHandler:
    def test_devuelve_lista_de_dtos(self) -> None:
        repo = MagicMock()
        repo.list_all.return_value = [_make_usuario("a@t.es"), _make_usuario("b@t.es")]
        handler = ListarUsuariosHandler(repo)
        dtos = handler.handle(ListarUsuariosQuery())
        assert len(dtos) == 2
        assert dtos[0].email == "a@t.es"

"""Tests unitarios del dominio Usuario (puros, sin I/O)."""

import pytest

from app.contexts.identity.domain.model import Rol, Usuario
from app.shared.domain.base import DomainError


def test_usuario_crear_valido() -> None:
    u = Usuario.crear("admin@ejemplo.es", "hash_seguro", Rol.ADMIN)
    assert u.email == "admin@ejemplo.es"
    assert u.rol == Rol.ADMIN
    assert u.activo is True


def test_usuario_email_invalido_sin_arroba() -> None:
    with pytest.raises(DomainError):
        Usuario.crear("sindominio", "hash", Rol.EDITOR)


def test_usuario_email_invalido_sin_dominio() -> None:
    with pytest.raises(DomainError):
        Usuario.crear("sin@", "hash", Rol.EDITOR)


def test_usuario_password_vacia_lanza_error() -> None:
    with pytest.raises(DomainError):
        Usuario.crear("ok@test.es", "", Rol.EDITOR)


def test_usuario_cambiar_password() -> None:
    u = Usuario.crear("u@test.es", "hash_viejo", Rol.EDITOR)
    evento = u.cambiar_password("hash_nuevo")
    assert u.hashed_password == "hash_nuevo"
    assert evento.usuario_id == u.id


def test_usuario_cambiar_password_vacia_lanza_error() -> None:
    u = Usuario.crear("u@test.es", "hash", Rol.EDITOR)
    with pytest.raises(DomainError):
        u.cambiar_password("")


def test_usuario_desactivar() -> None:
    u = Usuario.crear("u@test.es", "hash", Rol.EDITOR)
    u.desactivar()
    assert u.activo is False


def test_usuario_desactivar_ya_inactivo_lanza_error() -> None:
    u = Usuario.crear("u@test.es", "hash", Rol.EDITOR)
    u.desactivar()
    with pytest.raises(DomainError):
        u.desactivar()

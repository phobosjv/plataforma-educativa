"""Tests del servicio de autenticación (JWT con PyJWT, contraseñas con Argon2id)."""

from __future__ import annotations

import pytest

from app.contexts.identity.infrastructure.auth_service import ArgonAuthService
from app.shared.domain.base import AuthenticationError


def test_token_round_trip() -> None:
    auth = ArgonAuthService("secreto-de-test-suficientemente-largo-0123456789", 60)
    token = auth.create_access_token(subject="user-123", rol="admin")
    data = auth.decode_token(token)
    assert data["sub"] == "user-123"
    assert data["rol"] == "admin"


def test_token_invalido_lanza_error() -> None:
    auth = ArgonAuthService("secreto-de-test-suficientemente-largo-0123456789", 60)
    with pytest.raises(AuthenticationError):
        auth.decode_token("esto-no-es-un-jwt")


def test_token_con_secreto_distinto_lanza_error() -> None:
    emisor = ArgonAuthService("secreto-A-largo-0123456789-abcdefghij", 60)
    verificador = ArgonAuthService("secreto-B-largo-0123456789-abcdefghij", 60)
    token = emisor.create_access_token(subject="u", rol="editor")
    with pytest.raises(AuthenticationError):
        verificador.decode_token(token)


def test_token_expirado_lanza_error() -> None:
    # expire_minutes negativo -> el token nace ya caducado; PyJWT valida exp al decodificar.
    auth = ArgonAuthService("secreto-de-test-suficientemente-largo-0123456789", -1)
    token = auth.create_access_token(subject="u", rol="editor")
    with pytest.raises(AuthenticationError):
        auth.decode_token(token)


def test_password_hash_y_verify() -> None:
    auth = ArgonAuthService("secreto-de-test-suficientemente-largo-0123456789", 60)
    hashed = auth.hash_password("MiClave123")
    assert hashed != "MiClave123"  # nunca en claro
    assert auth.verify_password("MiClave123", hashed) is True
    assert auth.verify_password("incorrecta", hashed) is False

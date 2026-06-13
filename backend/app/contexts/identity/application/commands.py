"""Comandos (escritura) del contexto IDENTITY."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True)
class CrearUsuarioCommand:
    email: str
    password: str
    rol: str

"""Esquemas Pydantic de la API del contexto IDENTITY."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CrearUsuarioRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    rol: Literal["admin", "editor"]


class UsuarioResponse(BaseModel):
    id: UUID
    email: str
    rol: str
    activo: bool
    created_at: datetime

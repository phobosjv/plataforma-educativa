"""Esquemas Pydantic de la API del contexto CONTENIDO."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ContenidoResponse(BaseModel):
    id: UUID
    titulo: str
    descripcion: str
    tipo: str
    autor_id: UUID | None
    publicado: bool
    borrado: bool
    idioma: str
    etiquetas: list[str]
    hash_html: str | None
    body_html: str | None
    created_at: datetime
    updated_at: datetime


class CrearContenidoRequest(BaseModel):
    titulo: str = Field(min_length=1, max_length=500)
    descripcion: str = ""
    tipo: Literal["interactivo", "texto"]
    idioma: str = "es"
    etiquetas: list[str] = []
    body_html: str | None = None
    ciclo_id: UUID | None = None
    curso_id: UUID | None = None
    asignatura_id: UUID | None = None


class ActualizarContenidoRequest(BaseModel):
    titulo: str | None = Field(default=None, min_length=1, max_length=500)
    descripcion: str | None = None
    body_html: str | None = None
    etiquetas: list[str] | None = None

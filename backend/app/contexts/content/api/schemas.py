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
    ciclo_id: UUID | None
    curso_id: UUID | None
    asignatura_id: UUID | None
    hash_html: str | None
    body_html: str | None
    # URL absoluta del ejercicio en el origen sandbox (solo tipo interactivo con HTML subido).
    sandbox_url: str | None = None
    created_at: datetime
    updated_at: datetime


class VersionResponse(BaseModel):
    version_no: int
    titulo: str
    tipo: str
    created_by: UUID
    # Email del autor de la versión, resuelto en la capa API a partir de ``created_by``
    # (puede ser None si ese usuario ya no existe).
    created_by_email: str | None = None
    created_at: datetime


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
    # La clasificación puede reasignarse al editar. Para poder DESasignar (null) sin que
    # ello se confunda con "no tocar", el router usa model_fields_set (ver router.py).
    ciclo_id: UUID | None = None
    curso_id: UUID | None = None
    asignatura_id: UUID | None = None

"""Schemas Pydantic del contexto TAXONOMÍA."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class CicloResponse(BaseModel):
    id: UUID
    nombre: str
    orden: int


class CrearCicloRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    orden: int = Field(default=0, ge=0)


class ActualizarCicloRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    orden: int | None = Field(default=None, ge=0)


class CursoResponse(BaseModel):
    id: UUID
    nombre: str
    ciclo_id: UUID
    orden: int


class CrearCursoRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    ciclo_id: UUID
    orden: int = Field(default=0, ge=0)


class ActualizarCursoRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    orden: int | None = Field(default=None, ge=0)


class AsignaturaResponse(BaseModel):
    id: UUID
    nombre: str
    color: str


class CrearAsignaturaRequest(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    color: str = "#6366f1"


class ActualizarAsignaturaRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = None

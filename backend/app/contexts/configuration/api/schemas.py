from __future__ import annotations

from pydantic import BaseModel, Field


class PaletaResponse(BaseModel):
    id: str
    nombre: str
    bg: str
    surface: str
    fg: str
    primary: str


class ConfiguracionResponse(BaseModel):
    nombre_sitio: str
    paleta_activa: str
    paletas_personalizadas: list[PaletaResponse]


class ActivarPaletaRequest(BaseModel):
    paleta_id: str


class PaletaRequest(BaseModel):
    id: str
    nombre: str
    bg: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    surface: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    fg: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    primary: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")

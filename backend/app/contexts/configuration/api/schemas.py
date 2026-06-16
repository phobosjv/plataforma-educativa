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
    fuente_activa: str
    fondo_activo: str
    fondo_estilo: str
    aula_abierta_label: str
    aula_abierta_emoji: str
    paletas_personalizadas: list[PaletaResponse]


class AjustesGeneralesRequest(BaseModel):
    nombre_sitio: str = Field(min_length=1, max_length=80)
    fuente_activa: str
    fondo_activo: str = "ninguno"
    fondo_estilo: str = "ordenado"
    aula_abierta_label: str = Field(default="Aula Abierta", min_length=1, max_length=40)
    aula_abierta_emoji: str = Field(default="🌟", max_length=8)


class ActivarPaletaRequest(BaseModel):
    paleta_id: str


class PaletaRequest(BaseModel):
    id: str
    nombre: str
    bg: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    surface: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    fg: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    primary: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")

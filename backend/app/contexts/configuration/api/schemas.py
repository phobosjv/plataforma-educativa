from __future__ import annotations

from pydantic import BaseModel, Field


class PaletaResponse(BaseModel):
    id: str
    nombre: str
    bg: str
    surface: str
    fg: str
    primary: str


class DonacionResponse(BaseModel):
    etiqueta: str
    url: str


class DonacionRequest(BaseModel):
    etiqueta: str = Field(min_length=1, max_length=40)
    url: str = Field(min_length=1, max_length=500)


class ConfiguracionResponse(BaseModel):
    nombre_sitio: str
    paleta_activa: str
    fuente_activa: str
    fondo_activo: str
    fondo_estilo: str
    logo_url: str
    aula_abierta_label: str
    aula_abierta_emoji: str
    catalogo_titulo: str
    catalogo_subtitulo: str
    donaciones: list[DonacionResponse]
    publicidad_activa: bool
    publicidad_html_izquierda: str
    publicidad_html_derecha: str
    paletas_personalizadas: list[PaletaResponse]


class AjustesGeneralesRequest(BaseModel):
    nombre_sitio: str = Field(min_length=1, max_length=80)
    fuente_activa: str
    fondo_activo: str = "ninguno"
    fondo_estilo: str = "ordenado"
    logo_url: str = Field(default="", max_length=500)
    aula_abierta_label: str = Field(default="Aula Abierta", min_length=1, max_length=40)
    aula_abierta_emoji: str = Field(default="🌟", max_length=8)
    catalogo_titulo: str = Field(default="¿En qué curso estás?", min_length=1, max_length=120)
    catalogo_subtitulo: str = Field(default="Toca tu curso para ver las actividades", max_length=120)
    donaciones: list[DonacionRequest] = Field(default_factory=list)
    publicidad_activa: bool = False
    publicidad_html_izquierda: str = Field(default="", max_length=8000)
    publicidad_html_derecha: str = Field(default="", max_length=8000)


class ActivarPaletaRequest(BaseModel):
    paleta_id: str


class PaletaRequest(BaseModel):
    id: str
    nombre: str
    bg: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    surface: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    fg: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    primary: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")

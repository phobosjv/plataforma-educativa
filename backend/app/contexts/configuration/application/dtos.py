from __future__ import annotations

from dataclasses import dataclass

from app.contexts.configuration.domain.model import ConfiguracionSitio


@dataclass
class PaletaDTO:
    id: str
    nombre: str
    bg: str
    surface: str
    fg: str
    primary: str


@dataclass
class ConfiguracionDTO:
    nombre_sitio: str
    paleta_activa: str
    fuente_activa: str
    fondo_activo: str
    paletas_personalizadas: list[PaletaDTO]


def config_to_dto(c: ConfiguracionSitio) -> ConfiguracionDTO:
    return ConfiguracionDTO(
        nombre_sitio=c.nombre_sitio,
        paleta_activa=c.paleta_activa,
        fuente_activa=c.fuente_activa,
        fondo_activo=c.fondo_activo,
        paletas_personalizadas=[
            PaletaDTO(
                id=p.id,
                nombre=p.nombre,
                bg=p.bg,
                surface=p.surface,
                fg=p.fg,
                primary=p.primary,
            )
            for p in c.paletas_personalizadas
        ],
    )

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
class DonacionDTO:
    etiqueta: str
    url: str


@dataclass
class RedSocialDTO:
    red: str
    url: str


@dataclass
class ConfiguracionDTO:
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
    donaciones: list[DonacionDTO]
    redes_sociales: list[RedSocialDTO]
    publicidad_activa: bool
    publicidad_html_izquierda: str
    publicidad_html_derecha: str
    mostrar_version: bool
    paletas_personalizadas: list[PaletaDTO]


def config_to_dto(c: ConfiguracionSitio) -> ConfiguracionDTO:
    return ConfiguracionDTO(
        nombre_sitio=c.nombre_sitio,
        paleta_activa=c.paleta_activa,
        fuente_activa=c.fuente_activa,
        fondo_activo=c.fondo_activo,
        fondo_estilo=c.fondo_estilo,
        logo_url=c.logo_url,
        aula_abierta_label=c.aula_abierta_label,
        aula_abierta_emoji=c.aula_abierta_emoji,
        catalogo_titulo=c.catalogo_titulo,
        catalogo_subtitulo=c.catalogo_subtitulo,
        donaciones=[DonacionDTO(etiqueta=d.etiqueta, url=d.url) for d in c.donaciones],
        redes_sociales=[RedSocialDTO(red=r.red, url=r.url) for r in c.redes_sociales],
        publicidad_activa=c.publicidad_activa,
        publicidad_html_izquierda=c.publicidad_html_izquierda,
        publicidad_html_derecha=c.publicidad_html_derecha,
        mostrar_version=c.mostrar_version,
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

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ActualizarAjustesGeneralesCommand:
    nombre_sitio: str
    fuente_activa: str
    fondo_activo: str = "ninguno"
    fondo_estilo: str = "ordenado"
    logo_url: str = ""
    aula_abierta_label: str = "Aula Abierta"
    aula_abierta_emoji: str = "🌟"
    catalogo_titulo: str = "¿En qué curso estás?"
    catalogo_subtitulo: str = "Toca tu curso para ver las actividades"
    # Pares (etiqueta, url); tupla para que el command sea inmutable/hashable.
    donaciones: tuple[tuple[str, str], ...] = ()
    # Pares (red, url).
    redes_sociales: tuple[tuple[str, str], ...] = ()
    publicidad_activa: bool = False
    publicidad_html_izquierda: str = ""
    publicidad_html_derecha: str = ""
    mostrar_version: bool = True


@dataclass(frozen=True)
class ActivarPaletaCommand:
    paleta_id: str


@dataclass(frozen=True)
class AgregarPaletaCommand:
    id: str
    nombre: str
    bg: str
    surface: str
    fg: str
    primary: str


@dataclass(frozen=True)
class ActualizarPaletaCommand:
    id: str
    nombre: str
    bg: str
    surface: str
    fg: str
    primary: str


@dataclass(frozen=True)
class EliminarPaletaCommand:
    paleta_id: str

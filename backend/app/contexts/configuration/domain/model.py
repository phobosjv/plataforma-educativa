"""Modelo de dominio del contexto CONFIGURATION. SIN dependencias de framework."""

from __future__ import annotations

import json
from dataclasses import dataclass
from uuid import UUID

from app.shared.domain.base import DomainError, Entity

SINGLETON_ID = UUID("00000000-0000-0000-0000-000000000001")

# Catálogo de fuentes seleccionables. El identificador "sistema" usa la pila de
# fuentes nativa del dispositivo (sin descarga); el resto son fuentes self-hosted
# servidas por la propia app (no desde un CDN externo) para no exponer la IP de
# los menores a terceros (CLAUDE.md §10). El dominio solo conoce los IDs válidos;
# los ficheros y la familia CSS concreta viven en el frontend.
FUENTES_PERMITIDAS: frozenset[str] = frozenset(
    {"sistema", "nunito", "quicksand", "lexend", "atkinson", "andika"}
)

# Catálogo de fondos/estampados temáticos. "ninguno" deja el fondo liso. El resto
# son patrones SVG self-hosted (servidos por la app) que se recolorean con la paleta
# activa a baja opacidad. El dominio solo conoce los IDs válidos.
FONDOS_PERMITIDOS: frozenset[str] = frozenset(
    {"ninguno", "classroom", "naturaleza", "espacio", "oceano", "geometrico", "granja"}
)

# Disposición del estampado: "ordenado" repite el tile fijo; "desordenado" genera un
# patrón disperso (posición/rotación/escala variables) en el que dos iconos iguales nunca
# quedan adyacentes. El dominio solo conoce los IDs válidos; la generación vive en el frontend.
ESTILOS_FONDO_PERMITIDOS: frozenset[str] = frozenset({"ordenado", "desordenado"})

LONGITUD_MAX_NOMBRE = 80
LONGITUD_MAX_AULA_ABIERTA = 40
LONGITUD_MAX_EMOJI = 8


@dataclass
class PaletaPersonalizada:
    id: str
    nombre: str
    bg: str
    surface: str
    fg: str
    primary: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "bg": self.bg,
            "surface": self.surface,
            "fg": self.fg,
            "primary": self.primary,
        }


@dataclass
class ConfiguracionSitio(Entity):
    nombre_sitio: str = "Plataforma Educativa"
    paleta_activa: str = "cielo"
    paletas_json: str = "[]"
    fuente_activa: str = "sistema"
    fondo_activo: str = "ninguno"
    fondo_estilo: str = "ordenado"
    # Etiqueta y emoji de la entrada a las asignaturas transversales en el catálogo. El
    # nombre lo decide cada centro (p. ej. "Aula Abierta", "Diversidad") para evitar
    # términos que puedan estigmatizar al alumnado con esas necesidades.
    aula_abierta_label: str = "Aula Abierta"
    aula_abierta_emoji: str = "🌟"

    @classmethod
    def singleton(cls) -> "ConfiguracionSitio":
        return cls(id=SINGLETON_ID)

    @property
    def paletas_personalizadas(self) -> list[PaletaPersonalizada]:
        return [PaletaPersonalizada(**p) for p in json.loads(self.paletas_json)]

    def cambiar_nombre(self, nombre: str) -> None:
        nombre = nombre.strip()
        if not nombre:
            raise DomainError("El nombre del sitio no puede estar vacío.")
        if len(nombre) > LONGITUD_MAX_NOMBRE:
            raise DomainError(
                f"El nombre del sitio no puede superar {LONGITUD_MAX_NOMBRE} caracteres."
            )
        self.nombre_sitio = nombre

    def cambiar_fuente(self, fuente_id: str) -> None:
        if fuente_id not in FUENTES_PERMITIDAS:
            raise DomainError(f"Fuente '{fuente_id}' no permitida.")
        self.fuente_activa = fuente_id

    def cambiar_fondo(self, fondo_id: str) -> None:
        if fondo_id not in FONDOS_PERMITIDOS:
            raise DomainError(f"Fondo '{fondo_id}' no permitido.")
        self.fondo_activo = fondo_id

    def cambiar_estilo_fondo(self, estilo: str) -> None:
        if estilo not in ESTILOS_FONDO_PERMITIDOS:
            raise DomainError(f"Estilo de fondo '{estilo}' no permitido.")
        self.fondo_estilo = estilo

    def cambiar_aula_abierta(self, label: str, emoji: str) -> None:
        label = label.strip()
        if not label:
            raise DomainError("La etiqueta de Aula Abierta no puede estar vacía.")
        if len(label) > LONGITUD_MAX_AULA_ABIERTA:
            raise DomainError(
                f"La etiqueta de Aula Abierta no puede superar {LONGITUD_MAX_AULA_ABIERTA} caracteres."
            )
        emoji = emoji.strip()
        if len(emoji) > LONGITUD_MAX_EMOJI:
            raise DomainError("El emoji de Aula Abierta es demasiado largo.")
        self.aula_abierta_label = label
        self.aula_abierta_emoji = emoji

    def activar_paleta(self, paleta_id: str) -> None:
        self.paleta_activa = paleta_id

    def agregar_paleta(self, paleta: PaletaPersonalizada) -> None:
        paletas = self.paletas_personalizadas
        if any(p.id == paleta.id for p in paletas):
            raise DomainError(f"Ya existe una paleta con id '{paleta.id}'.")
        paletas.append(paleta)
        self.paletas_json = json.dumps([p.to_dict() for p in paletas])

    def actualizar_paleta(self, paleta: PaletaPersonalizada) -> None:
        paletas = [paleta if p.id == paleta.id else p for p in self.paletas_personalizadas]
        if not any(p.id == paleta.id for p in paletas):
            raise DomainError(f"Paleta '{paleta.id}' no encontrada.")
        self.paletas_json = json.dumps([p.to_dict() for p in paletas])

    def eliminar_paleta(self, paleta_id: str) -> None:
        if self.paleta_activa == paleta_id:
            raise DomainError("No se puede eliminar la paleta activa.")
        paletas = [p for p in self.paletas_personalizadas if p.id != paleta_id]
        self.paletas_json = json.dumps([p.to_dict() for p in paletas])

"""Modelo de dominio del contexto CONFIGURATION. SIN dependencias de framework."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from uuid import UUID

from app.shared.domain.base import DomainError, Entity

SINGLETON_ID = UUID("00000000-0000-0000-0000-000000000001")


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

    @classmethod
    def singleton(cls) -> "ConfiguracionSitio":
        return cls(id=SINGLETON_ID)

    @property
    def paletas_personalizadas(self) -> list[PaletaPersonalizada]:
        return [PaletaPersonalizada(**p) for p in json.loads(self.paletas_json)]

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

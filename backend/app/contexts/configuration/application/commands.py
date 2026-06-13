from __future__ import annotations

from dataclasses import dataclass


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

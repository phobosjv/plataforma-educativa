"""DTOs de la capa de aplicación del contexto ANALYTICS."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class VisitasDTO:
    total: int
    por_contenido: dict[UUID, int] = field(default_factory=dict)

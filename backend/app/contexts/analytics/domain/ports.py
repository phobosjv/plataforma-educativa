"""Puertos (interfaces) del contexto ANALYTICS. Los implementa la infraestructura.

El conteo de visitas sigue CLAUDE.md §8: se agrega en memoria (``BufferVisitas``) y se
vuelca por lotes a la persistencia (``VisitasRepository``) en una tarea de fondo; nunca se
escribe en la BD en cada petición. Las visitas son anónimas y agregadas (§10): solo se
guarda un total por contenido, sin datos del visitante.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol
from uuid import UUID


class BufferVisitas(Protocol):
    """Acumulador en memoria, seguro para concurrencia, de visitas pendientes de volcar."""

    def registrar(self, contenido_id: UUID, n: int = 1) -> None: ...

    def drenar(self) -> dict[UUID, int]:
        """Devuelve los conteos acumulados y deja el buffer a cero, de forma atómica."""
        ...

    def pendientes(self) -> int: ...


class VisitasRepository(Protocol):
    """Persistencia del total agregado de visitas por contenido."""

    def incrementar(self, conteos: Mapping[UUID, int]) -> None: ...

    def total_por_contenido(self) -> dict[UUID, int]: ...

    def total(self) -> int: ...

"""Casos de uso del contexto ANALYTICS: registrar, volcar y consultar visitas."""

from __future__ import annotations

from uuid import UUID

from app.contexts.analytics.application.dtos import VisitasDTO
from app.contexts.analytics.domain.ports import BufferVisitas, VisitasRepository
from app.shared.infrastructure.unit_of_work import UnitOfWork


class RegistrarVisitaHandler:
    """Anota una visita en el buffer en memoria (sin tocar la BD)."""

    def __init__(self, buffer: BufferVisitas) -> None:
        self._buffer = buffer

    def handle(self, contenido_id: UUID) -> None:
        self._buffer.registrar(contenido_id)


class VolcarVisitasHandler:
    """Vuelca a la BD, por lotes, las visitas acumuladas en el buffer.

    Drena el buffer y suma los conteos al total de cada contenido en una única transacción.
    Devuelve cuántas visitas se persistieron (útil para el log y los tests). Lo invoca la
    tarea de mantenimiento periódica; no se expone como endpoint.
    """

    def __init__(self, buffer: BufferVisitas, repo: VisitasRepository, uow: UnitOfWork) -> None:
        self._buffer = buffer
        self._repo = repo
        self._uow = uow

    def handle(self) -> int:
        conteos = self._buffer.drenar()
        if not conteos:
            return 0
        self._repo.incrementar(conteos)
        self._uow.commit()
        return sum(conteos.values())


class ObtenerVisitasHandler:
    """Consulta el total de visitas y el desglose por contenido (ya persistidos)."""

    def __init__(self, repo: VisitasRepository) -> None:
        self._repo = repo

    def handle(self) -> VisitasDTO:
        return VisitasDTO(total=self._repo.total(), por_contenido=self._repo.total_por_contenido())

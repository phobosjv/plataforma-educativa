"""Casos de uso del contexto ANALYTICS: registrar, volcar y consultar visitas."""

from __future__ import annotations

from uuid import UUID

from app.contexts.analytics.application.dtos import VisitasDTO
from app.contexts.analytics.domain.ports import (
    BufferVisitas,
    ContenidosConocidos,
    VisitasRepository,
)
from app.shared.infrastructure.unit_of_work import UnitOfWork


class RegistrarVisitaHandler:
    """Anota una visita en el buffer en memoria (sin tocar la BD)."""

    def __init__(self, buffer: BufferVisitas) -> None:
        self._buffer = buffer

    def handle(self, contenido_id: UUID) -> None:
        self._buffer.registrar(contenido_id)


class VolcarVisitasHandler:
    """Vuelca a la BD, por lotes, las visitas acumuladas en el buffer.

    Drena el buffer, descarta los conteos de contenido inexistente (UUID arbitrarios o ya
    purgado, para no crear filas huérfanas) y suma el resto al total de cada contenido en una
    única transacción. Si la persistencia falla, devuelve los conteos al buffer para no perder
    el lote (el próximo volcado lo reintenta). Lo invoca la tarea de mantenimiento periódica.
    """

    def __init__(
        self,
        buffer: BufferVisitas,
        repo: VisitasRepository,
        uow: UnitOfWork,
        contenidos: ContenidosConocidos,
    ) -> None:
        self._buffer = buffer
        self._repo = repo
        self._uow = uow
        self._contenidos = contenidos

    def handle(self) -> int:
        conteos = self._buffer.drenar()
        if not conteos:
            return 0
        existentes = self._contenidos.filtrar_existentes(set(conteos))
        validos = {cid: n for cid, n in conteos.items() if cid in existentes}
        if not validos:
            return 0
        try:
            self._repo.incrementar(validos)
            self._uow.commit()
        except Exception:
            # No perder el lote: devolver al buffer lo que íbamos a persistir y reintentar luego.
            for cid, n in validos.items():
                self._buffer.registrar(cid, n)
            raise
        return sum(validos.values())


class ObtenerVisitasHandler:
    """Consulta el total de visitas y el desglose por contenido (ya persistidos)."""

    def __init__(self, repo: VisitasRepository) -> None:
        self._repo = repo

    def handle(self) -> VisitasDTO:
        return VisitasDTO(total=self._repo.total(), por_contenido=self._repo.total_por_contenido())

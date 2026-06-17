"""Router del contexto ANALYTICS: registro (público) y consulta (admin) de visitas."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.contexts.analytics.api.schemas import VisitasResponse
from app.contexts.analytics.application.handlers import (
    ObtenerVisitasHandler,
    RegistrarVisitaHandler,
)
from app.contexts.analytics.infrastructure.buffer import buffer_visitas
from app.contexts.analytics.infrastructure.repositories import SqlAlchemyVisitasRepository
from app.contexts.identity.api.dependencies import require_admin
from app.shared.infrastructure.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/visitas/{contenido_id}", status_code=status.HTTP_204_NO_CONTENT)
def registrar_visita(contenido_id: UUID) -> None:
    """Anota una visita anónima a un contenido (público).

    Solo incrementa un contador en memoria; NO escribe en la BD (CLAUDE.md §8). La tarea de
    mantenimiento vuelca los conteos por lotes. Sin datos del visitante (§10).
    """
    RegistrarVisitaHandler(buffer_visitas).handle(contenido_id)


@router.get("/visitas", response_model=VisitasResponse, dependencies=[Depends(require_admin)])
def obtener_visitas(db: Session = Depends(get_db)) -> VisitasResponse:
    """Total de visitas y desglose por contenido (solo admin). Refleja lo ya volcado a la BD."""
    dto = ObtenerVisitasHandler(SqlAlchemyVisitasRepository(db)).handle()
    return VisitasResponse(
        total=dto.total,
        por_contenido={str(cid): n for cid, n in dto.por_contenido.items()},
    )

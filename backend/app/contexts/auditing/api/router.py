"""Router del contexto AUDITING: consulta del registro de auditoría (solo admin)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.contexts.auditing.api.schemas import AuditoriaEntradaResponse, AuditoriaListResponse
from app.contexts.auditing.application.handlers import ListarAuditoriaHandler
from app.contexts.auditing.infrastructure.repositories import SqlAlchemyAuditoriaRepository
from app.contexts.identity.api.dependencies import require_admin
from app.shared.infrastructure.database import get_db

router = APIRouter(prefix="/auditoria", tags=["auditing"])


@router.get("", response_model=AuditoriaListResponse, dependencies=[Depends(require_admin)])
def listar_auditoria(
    limite: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> AuditoriaListResponse:
    """Registro de acciones de gestión, más recientes primero (solo admin)."""
    entradas, total = ListarAuditoriaHandler(SqlAlchemyAuditoriaRepository(db)).handle(
        limite=limite, offset=offset
    )
    return AuditoriaListResponse(
        total=total,
        entradas=[
            AuditoriaEntradaResponse(
                id=str(e.id),
                usuario_id=str(e.usuario_id) if e.usuario_id else None,
                usuario_email=e.usuario_email,
                usuario_rol=e.usuario_rol,
                accion=e.accion,
                entidad=e.entidad,
                entidad_id=e.entidad_id,
                detalle=e.detalle,
                created_at=e.created_at,
            )
            for e in entradas
        ],
    )

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AuditoriaEntradaResponse(BaseModel):
    id: str
    usuario_id: str | None
    usuario_email: str
    usuario_rol: str
    accion: str
    entidad: str
    entidad_id: str | None
    detalle: str
    created_at: datetime


class AuditoriaListResponse(BaseModel):
    total: int
    entradas: list[AuditoriaEntradaResponse]

from __future__ import annotations

from pydantic import BaseModel


class VisitasResponse(BaseModel):
    total: int
    # contenido_id (str) -> nº de visitas acumuladas.
    por_contenido: dict[str, int]

"""Repositorio SQLAlchemy del contexto ANALYTICS (total de visitas por contenido)."""

from __future__ import annotations

from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.contexts.analytics.infrastructure.models import ContentViewsModel
from app.shared.domain.base import now


class SqlAlchemyVisitasRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def incrementar(self, conteos: Mapping[UUID, int]) -> None:
        """Suma los conteos al total de cada contenido (UPSERT atómico por fila).

        Usa ``INSERT ... ON CONFLICT DO UPDATE`` de SQLite: crea la fila la primera vez y
        acumula a partir de entonces. Pensado para volcados por lotes (no por petición).
        """
        momento = now()
        for contenido_id, n in conteos.items():
            if n <= 0:
                continue
            stmt = sqlite_insert(ContentViewsModel).values(
                content_id=str(contenido_id), total=n, updated_at=momento
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["content_id"],
                set_={"total": ContentViewsModel.total + n, "updated_at": momento},
            )
            self._session.execute(stmt)

    def total_por_contenido(self) -> dict[UUID, int]:
        rows = self._session.execute(
            select(ContentViewsModel.content_id, ContentViewsModel.total)
        ).all()
        return {UUID(content_id): total for content_id, total in rows}

    def total(self) -> int:
        return int(
            self._session.execute(
                select(func.coalesce(func.sum(ContentViewsModel.total), 0))
            ).scalar_one()
        )

"""Repositorio SQLAlchemy del contexto AUDITING."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.contexts.auditing.domain.model import EntradaAuditoria
from app.contexts.auditing.infrastructure.models import AuditLogModel


class SqlAlchemyAuditoriaRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def registrar(self, entrada: EntradaAuditoria) -> None:
        self._session.add(
            AuditLogModel(
                id=str(entrada.id),
                usuario_id=str(entrada.usuario_id) if entrada.usuario_id else None,
                usuario_email=entrada.usuario_email,
                usuario_rol=entrada.usuario_rol,
                accion=entrada.accion,
                entidad=entrada.entidad,
                entidad_id=entrada.entidad_id,
                detalle=entrada.detalle,
                created_at=entrada.created_at,
            )
        )

    def listar(self, limite: int = 200, offset: int = 0) -> list[EntradaAuditoria]:
        stmt = (
            select(AuditLogModel)
            .order_by(AuditLogModel.created_at.desc())
            .limit(limite)
            .offset(offset)
        )
        return [self._to_domain(m) for m in self._session.execute(stmt).scalars()]

    def contar(self) -> int:
        return int(self._session.execute(select(func.count(AuditLogModel.id))).scalar_one())

    @staticmethod
    def _to_domain(m: AuditLogModel) -> EntradaAuditoria:
        return EntradaAuditoria(
            id=UUID(m.id),
            usuario_id=UUID(m.usuario_id) if m.usuario_id else None,
            usuario_email=m.usuario_email,
            usuario_rol=m.usuario_rol,
            accion=m.accion,
            entidad=m.entidad,
            entidad_id=m.entidad_id,
            detalle=m.detalle,
            created_at=m.created_at,
        )

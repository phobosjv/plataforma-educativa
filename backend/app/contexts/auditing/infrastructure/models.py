"""Modelo ORM del contexto AUDITING: registro de acciones de gestión (append-only)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.database import Base


class AuditLogModel(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(primary_key=True)
    usuario_id: Mapped[str | None] = mapped_column(nullable=True)
    usuario_email: Mapped[str] = mapped_column(nullable=False, default="")
    usuario_rol: Mapped[str] = mapped_column(nullable=False, default="")
    accion: Mapped[str] = mapped_column(nullable=False)
    entidad: Mapped[str] = mapped_column(nullable=False)
    entidad_id: Mapped[str | None] = mapped_column(nullable=True)
    detalle: Mapped[str] = mapped_column(nullable=False, default="")
    # Indexado: el registro se consulta y ordena por fecha (más reciente primero).
    created_at: Mapped[datetime] = mapped_column(nullable=False, index=True)

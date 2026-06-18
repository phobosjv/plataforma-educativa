"""Modelos ORM del contexto CONTENIDO. Nombres de columna en inglés (convención infra)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.infrastructure.database import Base


class ContenidoModel(Base):
    __tablename__ = "content"

    id: Mapped[str] = mapped_column(primary_key=True)
    tipo: Mapped[str] = mapped_column(nullable=False)
    titulo: Mapped[str] = mapped_column(nullable=False)
    descripcion: Mapped[str] = mapped_column(nullable=False, default="")
    autor_id: Mapped[str | None] = mapped_column(nullable=True)
    # FK con ON DELETE RESTRICT: la BD impide borrar una taxonomía referenciada por contenido
    # (refuerza, a nivel de motor, la guarda de dominio de los handlers de borrado).
    ciclo_id: Mapped[str | None] = mapped_column(
        ForeignKey("ciclo.id", ondelete="RESTRICT"), nullable=True
    )
    curso_id: Mapped[str | None] = mapped_column(
        ForeignKey("curso.id", ondelete="RESTRICT"), nullable=True
    )
    asignatura_id: Mapped[str | None] = mapped_column(
        ForeignKey("asignatura.id", ondelete="RESTRICT"), nullable=True
    )
    idioma: Mapped[str] = mapped_column(nullable=False, default="es")
    is_published: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_exam: Mapped[bool] = mapped_column(nullable=False, default=False)
    hash_html: Mapped[str | None] = mapped_column(nullable=True)
    body_html: Mapped[str | None] = mapped_column(nullable=True)
    tags_json: Mapped[str] = mapped_column(nullable=False, default="[]")
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

    versions: Mapped[list["ContentVersionModel"]] = relationship(
        back_populates="contenido", cascade="all, delete-orphan"
    )


class ContentVersionModel(Base):
    __tablename__ = "content_version"
    __table_args__ = (UniqueConstraint("content_id", "version_no"),)

    id: Mapped[str] = mapped_column(primary_key=True)
    content_id: Mapped[str] = mapped_column(ForeignKey("content.id"), index=True, nullable=False)
    version_no: Mapped[int] = mapped_column(nullable=False)
    metadata_snapshot_json: Mapped[str] = mapped_column(nullable=False)
    body_html: Mapped[str | None] = mapped_column(nullable=True)
    hash_html: Mapped[str | None] = mapped_column(nullable=True)
    created_by: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)

    contenido: Mapped["ContenidoModel"] = relationship(back_populates="versions")

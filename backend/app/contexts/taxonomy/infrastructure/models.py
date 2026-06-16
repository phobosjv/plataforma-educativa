"""Modelos ORM SQLAlchemy del contexto TAXONOMÍA."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.database import Base


class CicloModel(Base):
    __tablename__ = "ciclo"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class CursoModel(Base):
    __tablename__ = "curso"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    ciclo_id: Mapped[str] = mapped_column(String, ForeignKey("ciclo.id"), nullable=False)
    orden: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class AsignaturaModel(Base):
    __tablename__ = "asignatura"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, default="#6366f1", nullable=False)
    is_transversal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

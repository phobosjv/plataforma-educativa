"""Modelo ORM del contexto ANALYTICS: total agregado de visitas por contenido."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.database import Base


class ContentViewsModel(Base):
    __tablename__ = "content_views"

    # Una fila por contenido visitado. No es FK a content: si un contenido se purga, su
    # fila de visitas queda huérfana (inocua) y la lectura la cruza con el catálogo.
    content_id: Mapped[str] = mapped_column(primary_key=True)
    total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)

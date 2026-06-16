from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.infrastructure.database import Base


class ConfiguracionModel(Base):
    __tablename__ = "site_config"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    nombre_sitio: Mapped[str] = mapped_column(String(255), default="Plataforma Educativa")
    paleta_activa: Mapped[str] = mapped_column(String(100), default="cielo")
    paletas_json: Mapped[str] = mapped_column(Text, default="[]")
    fuente_activa: Mapped[str] = mapped_column(String(100), default="sistema")
    fondo_activo: Mapped[str] = mapped_column(String(100), default="ninguno")
    fondo_estilo: Mapped[str] = mapped_column(String(100), default="ordenado")
    aula_abierta_label: Mapped[str] = mapped_column(String(40), default="Aula Abierta")
    aula_abierta_emoji: Mapped[str] = mapped_column(String(16), default="🌟")

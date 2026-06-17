"""Modelo de dominio del contexto AUDITING. SIN dependencias de framework.

Una ``EntradaAuditoria`` es un registro inmutable de una acción de gestión (admin/editor):
quién la hizo, qué hizo, sobre qué objeto y cuándo. El registro es de solo-añadir
(append-only): nunca se edita ni se borra desde la aplicación.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.shared.domain.base import Entity, now


@dataclass
class EntradaAuditoria(Entity):
    usuario_id: UUID | None = None
    usuario_email: str = ""
    usuario_rol: str = ""
    accion: str = ""  # p. ej. "crear", "editar", "publicar", "borrar", "purgar"
    entidad: str = ""  # p. ej. "contenido", "usuario", "ciclo", "configuracion"
    entidad_id: str | None = None
    detalle: str = ""  # texto libre opcional (p. ej. el título del contenido)
    created_at: datetime = field(default_factory=now)

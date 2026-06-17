"""Punto de entrada para registrar auditoría desde la capa API de otros contextos.

Los routers de gestión llaman a ``registrar_auditoria(...)`` tras una acción con éxito,
con la MISMA sesión de la petición (así la entrada es coherente y los tests la ven). Toma
datos primitivos del usuario (id/email/rol) para no acoplar ``auditing`` a ``identity``.

Es deliberadamente "a prueba de fallos": si registrar la auditoría falla, se traga el error
(se loguea) y NUNCA tumba la acción real del usuario; la auditoría es secundaria.
"""

from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.contexts.auditing.application.handlers import RegistrarAuditoriaHandler
from app.contexts.auditing.domain.model import EntradaAuditoria
from app.contexts.auditing.infrastructure.repositories import SqlAlchemyAuditoriaRepository
from app.shared.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


def registrar_auditoria(
    db: Session,
    *,
    usuario_id: UUID | None,
    usuario_email: str,
    usuario_rol: str,
    accion: str,
    entidad: str,
    entidad_id: str | None = None,
    detalle: str = "",
) -> None:
    entrada = EntradaAuditoria(
        usuario_id=usuario_id,
        usuario_email=usuario_email,
        usuario_rol=usuario_rol,
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        detalle=detalle,
    )
    try:
        RegistrarAuditoriaHandler(SqlAlchemyAuditoriaRepository(db), UnitOfWork(db)).handle(entrada)
    except Exception:  # noqa: BLE001 — la auditoría jamás debe romper la acción del usuario.
        logger.exception("No se pudo registrar la auditoría de '%s %s'.", accion, entidad)

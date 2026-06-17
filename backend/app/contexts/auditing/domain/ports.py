"""Puertos (interfaces) del contexto AUDITING. Los implementa la infraestructura."""

from __future__ import annotations

from typing import Protocol

from app.contexts.auditing.domain.model import EntradaAuditoria


class AuditoriaRepository(Protocol):
    def registrar(self, entrada: EntradaAuditoria) -> None: ...

    def listar(self, limite: int = 200, offset: int = 0) -> list[EntradaAuditoria]:
        """Entradas más recientes primero."""
        ...

    def contar(self) -> int: ...

"""Casos de uso del contexto AUDITING: registrar y listar entradas."""

from __future__ import annotations

from app.contexts.auditing.application.dtos import AuditoriaDTO, entrada_to_dto
from app.contexts.auditing.domain.model import EntradaAuditoria
from app.contexts.auditing.domain.ports import AuditoriaRepository
from app.shared.infrastructure.unit_of_work import UnitOfWork


class RegistrarAuditoriaHandler:
    """Persiste una entrada de auditoría (append-only)."""

    def __init__(self, repo: AuditoriaRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, entrada: EntradaAuditoria) -> None:
        self._repo.registrar(entrada)
        self._uow.commit()


class ListarAuditoriaHandler:
    """Lista las entradas más recientes y el total (para la página de admin)."""

    def __init__(self, repo: AuditoriaRepository) -> None:
        self._repo = repo

    def handle(self, limite: int = 200, offset: int = 0) -> tuple[list[AuditoriaDTO], int]:
        entradas = [entrada_to_dto(e) for e in self._repo.listar(limite=limite, offset=offset)]
        return entradas, self._repo.contar()

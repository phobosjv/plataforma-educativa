"""Tareas de mantenimiento en segundo plano (sin broker, en proceso).

Coherente con CLAUDE.md §3 (eventos/tareas en proceso, sin broker) y con el patrón ya
previsto para el volcado por lotes del contador de visitas. Arranca con el ciclo de vida
de FastAPI (``lifespan``) y se detiene limpiamente al apagar la app.

Dos tareas periódicas:
- **Backup** de la BD SQLite (copia en caliente + rotación).
- **Purga** del contenido vencido en la papelera (borrado lógico -> físico).

Las operaciones de E/S y BD son síncronas; se ejecutan en un hilo (``asyncio.to_thread``)
para no bloquear el bucle de eventos.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from app.config import Settings
from app.contexts.content.application.commands import PurgarPapeleraVencidaCommand
from app.contexts.content.application.handlers import PurgarPapeleraVencidaHandler
from app.contexts.content.infrastructure.repositories import SqlAlchemyContenidoRepository
from app.shared.infrastructure.backup import SqliteBackupService
from app.shared.infrastructure.database import SessionLocal
from app.shared.infrastructure.media_backup import MediaMirrorService
from app.shared.infrastructure.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


def _ejecutar_backup(settings: Settings) -> None:
    SqliteBackupService(
        settings.database_url, settings.backup_dir, settings.backup_keep
    ).crear_backup()
    # Copia incremental de media en el mismo ciclo (solo ficheros nuevos; son inmutables).
    if settings.media_backup_enabled:
        mirror_dir = str(Path(settings.backup_dir) / "media")
        MediaMirrorService(settings.media_dir, mirror_dir).sync()


def _ejecutar_purga(settings: Settings) -> None:
    session = SessionLocal()
    try:
        repo = SqlAlchemyContenidoRepository(session)
        handler = PurgarPapeleraVencidaHandler(repo, UnitOfWork(session))
        purgados = handler.handle(
            PurgarPapeleraVencidaCommand(antiguedad_dias=settings.trash_retention_days)
        )
        if purgados:
            logger.info("Purga de papelera: %d contenido(s) eliminados definitivamente.", purgados)
    finally:
        session.close()


class MaintenanceScheduler:
    """Lanza y detiene las tareas periódicas de backup y purga."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._tasks: list[asyncio.Task[None]] = []
        self._stop = asyncio.Event()

    def start(self) -> None:
        s = self._settings
        if s.backup_enabled:
            self._programar(
                "backup",
                lambda: asyncio.to_thread(_ejecutar_backup, s),
                intervalo_horas=s.backup_interval_hours,
            )
        if s.trash_purge_enabled and s.trash_retention_days > 0:
            self._programar(
                "purga-papelera",
                lambda: asyncio.to_thread(_ejecutar_purga, s),
                intervalo_horas=s.trash_purge_interval_hours,
            )

    async def stop(self) -> None:
        self._stop.set()
        for t in self._tasks:
            t.cancel()
        for t in self._tasks:
            try:
                await t
            except asyncio.CancelledError:
                pass

    def _programar(
        self, nombre: str, accion: Callable[[], Awaitable[None]], intervalo_horas: int
    ) -> None:
        intervalo = max(1, intervalo_horas) * 3600
        self._tasks.append(asyncio.create_task(self._bucle(nombre, accion, intervalo)))

    async def _bucle(
        self, nombre: str, accion: Callable[[], Awaitable[None]], intervalo_seg: float
    ) -> None:
        """Ejecuta la acción al arrancar y luego cada ``intervalo_seg``, hasta el stop.

        Un fallo de una iteración se registra pero no detiene la tarea: la siguiente
        vuelta lo reintenta. Así un error puntual de E/S no deja la app sin backups.
        """
        while not self._stop.is_set():
            try:
                await accion()
            except Exception:  # noqa: BLE001 — una tarea de fondo nunca debe morir por un fallo.
                logger.exception("Fallo en la tarea de mantenimiento '%s'.", nombre)
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=intervalo_seg)
            except asyncio.TimeoutError:
                pass  # venció el intervalo: toca otra iteración

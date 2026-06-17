"""Buffer en memoria de visitas (implementación del puerto ``BufferVisitas``).

Acumula los conteos de visitas en proceso, sin tocar la BD. Una tarea de fondo los vuelca
por lotes periódicamente (CLAUDE.md §8). Es seguro para concurrencia: el servidor puede
atender varias peticiones a la vez y el volcado lee/limpia el buffer de forma atómica.

Se expone una instancia ``buffer_visitas`` a nivel de módulo: es el singleton de proceso
que comparten el endpoint que registra visitas y la tarea que las vuelca.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from uuid import UUID


class BufferVisitasEnMemoria:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._conteos: dict[UUID, int] = defaultdict(int)

    def registrar(self, contenido_id: UUID, n: int = 1) -> None:
        if n <= 0:
            return
        with self._lock:
            self._conteos[contenido_id] += n

    def drenar(self) -> dict[UUID, int]:
        with self._lock:
            drenados = dict(self._conteos)
            self._conteos.clear()
            return drenados

    def pendientes(self) -> int:
        with self._lock:
            return sum(self._conteos.values())


# Singleton de proceso compartido por el endpoint de registro y la tarea de volcado.
buffer_visitas = BufferVisitasEnMemoria()

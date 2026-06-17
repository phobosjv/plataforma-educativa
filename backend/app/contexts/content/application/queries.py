"""Queries (lectura) del contexto CONTENIDO."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ObtenerContenidoQuery:
    contenido_id: UUID


@dataclass(frozen=True)
class ListarContenidosQuery:
    solo_publicados: bool = True
    tipo: str | None = None
    incluir_borrados: bool = False


@dataclass(frozen=True)
class BuscarContenidosQuery:
    texto: str
    solo_publicados: bool = True


@dataclass(frozen=True)
class ListarVersionesQuery:
    contenido_id: UUID

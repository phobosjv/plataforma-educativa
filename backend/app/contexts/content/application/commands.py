"""Comandos (escritura) del contexto CONTENIDO."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CrearContenidoCommand:
    titulo: str
    tipo: str
    autor_id: UUID
    descripcion: str = ""
    idioma: str = "es"
    etiquetas: tuple[str, ...] = ()
    ciclo_id: UUID | None = None
    curso_id: UUID | None = None
    asignatura_id: UUID | None = None
    body_html: str | None = None
    es_examen: bool = False


@dataclass(frozen=True)
class ActualizarContenidoCommand:
    contenido_id: UUID
    editor_id: UUID
    titulo: str | None = None
    descripcion: str | None = None
    body_html: str | None = None
    etiquetas: tuple[str, ...] | None = None
    es_examen: bool | None = None
    # La taxonomía solo se aplica si actualizar_taxonomia es True (permite asignar y desasignar
    # sin confundir "poner a null" con "no tocar").
    actualizar_taxonomia: bool = False
    ciclo_id: UUID | None = None
    curso_id: UUID | None = None
    asignatura_id: UUID | None = None


@dataclass(frozen=True)
class SubirHtmlContenidoCommand:
    contenido_id: UUID
    editor_id: UUID
    raw_html: bytes


@dataclass(frozen=True)
class PublicarContenidoCommand:
    contenido_id: UUID
    published_by: UUID


@dataclass(frozen=True)
class ArchivarContenidoCommand:
    contenido_id: UUID


@dataclass(frozen=True)
class BorrarContenidoCommand:
    contenido_id: UUID
    deleted_by: UUID


@dataclass(frozen=True)
class RestaurarContenidoCommand:
    contenido_id: UUID
    restored_by: UUID


@dataclass(frozen=True)
class RestaurarVersionCommand:
    """Restaura un contenido al estado de una de sus versiones anteriores.

    Restaurar NUNCA destruye historial (CLAUDE.md §7): aplica el snapshot de la versión
    indicada al contenido y crea una versión NUEVA con ese estado.
    """

    contenido_id: UUID
    version_no: int
    editor_id: UUID


@dataclass(frozen=True)
class PurgarContenidoCommand:
    """Eliminación DEFINITIVA de un contenido de la papelera (irreversible)."""

    contenido_id: UUID
    purged_by: UUID


@dataclass(frozen=True)
class PurgarPapeleraVencidaCommand:
    """Purga DEFINITIVA del contenido que lleva en papelera más de ``antiguedad_dias``.

    Operación de mantenimiento sin actor humano (la dispara la tarea programada). No
    lleva ``purged_by`` porque la ejecuta el sistema, no un usuario.
    """

    antiguedad_dias: int

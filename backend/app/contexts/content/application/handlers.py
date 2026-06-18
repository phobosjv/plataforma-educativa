"""Handlers de comandos y queries del contexto CONTENIDO."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from app.contexts.content.application.commands import (
    ActualizarContenidoCommand,
    ArchivarContenidoCommand,
    BorrarContenidoCommand,
    CrearContenidoCommand,
    PublicarContenidoCommand,
    PurgarContenidoCommand,
    PurgarPapeleraVencidaCommand,
    RestaurarContenidoCommand,
    RestaurarVersionCommand,
    SubirHtmlContenidoCommand,
)
from app.contexts.content.application.dtos import (
    ContenidoDTO,
    VersionDTO,
    contenido_to_dto,
    version_to_dto,
)
from app.contexts.content.application.queries import (
    BuscarContenidosQuery,
    ListarContenidosQuery,
    ListarVersionesQuery,
    ObtenerContenidoQuery,
)
from app.contexts.content.domain.model import ContentVersion, Contenido, TipoContenido
from app.contexts.content.domain.ports import (
    ContenidoRepository,
    ContentVersionRepository,
    HtmlSanitizer,
    HtmlStorage,
)
from app.shared.domain.base import DomainError, NotFoundError, now
from app.shared.infrastructure.unit_of_work import UnitOfWork


def _make_version(contenido: Contenido, version_no: int, created_by: UUID) -> ContentVersion:
    snapshot = {
        "titulo": contenido.titulo,
        "descripcion": contenido.descripcion,
        "tipo": contenido.tipo.value,
        "idioma": contenido.idioma,
        "etiquetas": list(contenido.etiquetas),
    }
    return ContentVersion(
        contenido_id=contenido.id,
        version_no=version_no,
        metadata_snapshot=snapshot,
        created_by=created_by,
        body_html=contenido.body_html,
        hash_html=contenido.hash_html,
    )


class CrearContenidoHandler:
    def __init__(
        self,
        repo: ContenidoRepository,
        version_repo: ContentVersionRepository,
        uow: UnitOfWork,
        sanitizer: HtmlSanitizer,
    ) -> None:
        self._repo = repo
        self._version_repo = version_repo
        self._uow = uow
        self._sanitizer = sanitizer

    def handle(self, cmd: CrearContenidoCommand) -> UUID:
        tipo = TipoContenido(cmd.tipo)
        body_html = cmd.body_html
        # Artículos de texto: SIEMPRE sanitizar en servidor (CLAUDE.md §10).
        if tipo is TipoContenido.TEXTO and body_html is not None:
            body_html = self._sanitizer.sanitize(body_html)
        contenido = Contenido(
            titulo=cmd.titulo,
            descripcion=cmd.descripcion,
            autor_id=cmd.autor_id,
            tipo=tipo,
            ciclo_id=cmd.ciclo_id,
            curso_id=cmd.curso_id,
            asignatura_id=cmd.asignatura_id,
            idioma=cmd.idioma,
            etiquetas=list(cmd.etiquetas),
            body_html=body_html,
            es_examen=cmd.es_examen,
        )
        version = _make_version(contenido, version_no=1, created_by=cmd.autor_id)
        self._repo.add(contenido)
        self._version_repo.add(version)
        self._uow.commit()
        return contenido.id


class ActualizarContenidoHandler:
    def __init__(
        self,
        repo: ContenidoRepository,
        version_repo: ContentVersionRepository,
        uow: UnitOfWork,
        sanitizer: HtmlSanitizer,
    ) -> None:
        self._repo = repo
        self._version_repo = version_repo
        self._uow = uow
        self._sanitizer = sanitizer

    def handle(self, cmd: ActualizarContenidoCommand) -> ContenidoDTO:
        contenido = self._repo.get(cmd.contenido_id)
        if contenido is None:
            raise NotFoundError(f"Contenido {cmd.contenido_id} no encontrado.")
        if contenido.borrado:
            raise NotFoundError("No se puede actualizar un contenido en la papelera.")

        if cmd.titulo is not None:
            contenido.titulo = cmd.titulo
        if cmd.descripcion is not None:
            contenido.descripcion = cmd.descripcion
        if cmd.body_html is not None:
            # Artículos de texto: SIEMPRE sanitizar en servidor (CLAUDE.md §10).
            contenido.body_html = (
                self._sanitizer.sanitize(cmd.body_html)
                if contenido.tipo is TipoContenido.TEXTO
                else cmd.body_html
            )
        if cmd.etiquetas is not None:
            contenido.etiquetas = list(cmd.etiquetas)
        if cmd.es_examen is not None:
            contenido.marcar_examen(cmd.es_examen)
        if cmd.actualizar_taxonomia:
            contenido.ciclo_id = cmd.ciclo_id
            contenido.curso_id = cmd.curso_id
            contenido.asignatura_id = cmd.asignatura_id
        contenido.updated_at = now()

        versiones = self._version_repo.list_for_contenido(cmd.contenido_id)
        version = _make_version(contenido, version_no=len(versiones) + 1, created_by=cmd.editor_id)
        self._repo.save(contenido)
        self._version_repo.add(version)
        self._uow.commit()
        return contenido_to_dto(contenido)


class SubirHtmlContenidoHandler:
    """Sube el fichero HTML de un ejercicio interactivo y lo asocia por hash.

    El HTML de ejercicios NO se sanea (CLAUDE.md §10): su aislamiento lo garantiza el
    iframe sandbox servido desde un origen distinto. Cada subida crea una versión nueva.
    """

    def __init__(
        self,
        repo: ContenidoRepository,
        version_repo: ContentVersionRepository,
        uow: UnitOfWork,
        storage: HtmlStorage,
    ) -> None:
        self._repo = repo
        self._version_repo = version_repo
        self._uow = uow
        self._storage = storage

    def handle(self, cmd: SubirHtmlContenidoCommand) -> ContenidoDTO:
        contenido = self._repo.get(cmd.contenido_id)
        if contenido is None or contenido.borrado:
            raise NotFoundError(f"Contenido {cmd.contenido_id} no encontrado.")

        file_hash = self._storage.save(cmd.raw_html)  # content-addressed, sin sanear
        contenido.adjuntar_html_interactivo(file_hash)
        contenido.updated_at = now()

        versiones = self._version_repo.list_for_contenido(cmd.contenido_id)
        version = _make_version(contenido, version_no=len(versiones) + 1, created_by=cmd.editor_id)
        self._repo.save(contenido)
        self._version_repo.add(version)
        self._uow.commit()
        return contenido_to_dto(contenido)


class PublicarContenidoHandler:
    def __init__(self, repo: ContenidoRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: PublicarContenidoCommand) -> ContenidoDTO:
        contenido = self._repo.get(cmd.contenido_id)
        if contenido is None:
            raise NotFoundError(f"Contenido {cmd.contenido_id} no encontrado.")
        contenido.publicar()
        contenido.updated_at = now()
        self._repo.save(contenido)
        self._uow.commit()
        return contenido_to_dto(contenido)


class ArchivarContenidoHandler:
    def __init__(self, repo: ContenidoRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: ArchivarContenidoCommand) -> None:
        contenido = self._repo.get(cmd.contenido_id)
        if contenido is None:
            raise NotFoundError(f"Contenido {cmd.contenido_id} no encontrado.")
        contenido.archivar()
        contenido.updated_at = now()
        self._repo.save(contenido)
        self._uow.commit()


class BorrarContenidoHandler:
    def __init__(self, repo: ContenidoRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: BorrarContenidoCommand) -> None:
        contenido = self._repo.get(cmd.contenido_id)
        if contenido is None:
            raise NotFoundError(f"Contenido {cmd.contenido_id} no encontrado.")
        contenido.borrar()
        contenido.updated_at = now()
        self._repo.save(contenido)
        self._uow.commit()


class RestaurarContenidoHandler:
    def __init__(self, repo: ContenidoRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: RestaurarContenidoCommand) -> ContenidoDTO:
        contenido = self._repo.get(cmd.contenido_id)
        if contenido is None:
            raise NotFoundError(f"Contenido {cmd.contenido_id} no encontrado.")
        contenido.restaurar()
        contenido.updated_at = now()
        self._repo.save(contenido)
        self._uow.commit()
        return contenido_to_dto(contenido)


class ListarVersionesHandler:
    """Lista las versiones (snapshots) de un contenido, de la más antigua a la más reciente."""

    def __init__(self, version_repo: ContentVersionRepository) -> None:
        self._version_repo = version_repo

    def handle(self, query: ListarVersionesQuery) -> list[VersionDTO]:
        versiones = self._version_repo.list_for_contenido(query.contenido_id)
        return [version_to_dto(v) for v in versiones]


class RestaurarVersionHandler:
    """Restaura un contenido al estado de una versión anterior, sin destruir historial.

    Aplica el snapshot de la versión indicada al contenido y crea una versión NUEVA con ese
    estado (CLAUDE.md §7: "restaurar nunca destruye"). Así el historial sigue creciendo y la
    operación es reversible (se puede volver a cualquier versión, incluida la previa).
    """

    def __init__(
        self,
        repo: ContenidoRepository,
        version_repo: ContentVersionRepository,
        uow: UnitOfWork,
    ) -> None:
        self._repo = repo
        self._version_repo = version_repo
        self._uow = uow

    def handle(self, cmd: RestaurarVersionCommand) -> ContenidoDTO:
        contenido = self._repo.get(cmd.contenido_id)
        if contenido is None or contenido.borrado:
            raise NotFoundError(f"Contenido {cmd.contenido_id} no encontrado.")

        versiones = self._version_repo.list_for_contenido(cmd.contenido_id)
        objetivo = next((v for v in versiones if v.version_no == cmd.version_no), None)
        if objetivo is None:
            raise NotFoundError(f"Versión {cmd.version_no} no encontrada.")

        snap = objetivo.metadata_snapshot
        contenido.titulo = str(snap.get("titulo", contenido.titulo))
        contenido.descripcion = str(snap.get("descripcion", contenido.descripcion))
        contenido.idioma = str(snap.get("idioma", contenido.idioma))
        contenido.etiquetas = list(snap.get("etiquetas", contenido.etiquetas))
        contenido.body_html = objetivo.body_html
        contenido.hash_html = objetivo.hash_html
        contenido.updated_at = now()

        version = _make_version(
            contenido, version_no=len(versiones) + 1, created_by=cmd.editor_id
        )
        self._repo.save(contenido)
        self._version_repo.add(version)
        self._uow.commit()
        return contenido_to_dto(contenido)


class PurgarContenidoHandler:
    """Elimina DEFINITIVAMENTE un contenido (y sus versiones por cascada) de la papelera.

    Solo se permite purgar contenido que ya está en la papelera (borrado lógico previo),
    para que la eliminación irreversible sea siempre un acto deliberado en dos pasos
    (CLAUDE.md §7: borrar es lógico; la purga es una operación explícita).
    """

    def __init__(self, repo: ContenidoRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: PurgarContenidoCommand) -> None:
        contenido = self._repo.get(cmd.contenido_id)
        if contenido is None:
            raise NotFoundError(f"Contenido {cmd.contenido_id} no encontrado.")
        if not contenido.borrado:
            raise DomainError("Solo se puede eliminar definitivamente un contenido de la papelera.")
        self._repo.delete_permanent(cmd.contenido_id)
        self._uow.commit()


class PurgarPapeleraVencidaHandler:
    """Elimina DEFINITIVAMENTE el contenido que lleva en papelera más de N días.

    Lo ejecuta la tarea de mantenimiento en segundo plano (no un usuario). Reúne el
    contenido cuya antigüedad en papelera supera el umbral y lo purga en un único commit.
    Devuelve cuántos elementos se purgaron (útil para el log y los tests).
    """

    def __init__(self, repo: ContenidoRepository, uow: UnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def handle(self, cmd: PurgarPapeleraVencidaCommand) -> int:
        if cmd.antiguedad_dias <= 0:
            return 0
        limite = now() - timedelta(days=cmd.antiguedad_dias)
        vencidos = self._repo.list_trash_borrado_antes_de(limite)
        for contenido in vencidos:
            self._repo.delete_permanent(contenido.id)
        if vencidos:
            self._uow.commit()
        return len(vencidos)


class ObtenerContenidoHandler:
    def __init__(self, repo: ContenidoRepository) -> None:
        self._repo = repo

    def handle(self, query: ObtenerContenidoQuery) -> ContenidoDTO:
        contenido = self._repo.get(query.contenido_id)
        if contenido is None or contenido.borrado:
            raise NotFoundError(f"Contenido {query.contenido_id} no encontrado.")
        return contenido_to_dto(contenido)


class BuscarContenidosHandler:
    """Busca contenidos por texto libre (título, descripción y etiquetas) vía FTS5."""

    def __init__(self, repo: ContenidoRepository) -> None:
        self._repo = repo

    def handle(self, query: BuscarContenidosQuery) -> list[ContenidoDTO]:
        items = self._repo.buscar(query.texto, solo_publicados=query.solo_publicados)
        return [contenido_to_dto(c) for c in items]


class ListarContenidosHandler:
    def __init__(self, repo: ContenidoRepository) -> None:
        self._repo = repo

    def handle(self, query: ListarContenidosQuery) -> list[ContenidoDTO]:
        if query.incluir_borrados:
            items = self._repo.list_trash()
            items += self._repo.list_all()
        elif query.solo_publicados:
            items = self._repo.list_published()
        else:
            items = self._repo.list_all()

        if query.tipo:
            items = [c for c in items if c.tipo.value == query.tipo]

        return [contenido_to_dto(c) for c in items]

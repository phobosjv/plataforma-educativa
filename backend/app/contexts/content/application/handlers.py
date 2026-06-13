"""Handlers de comandos y queries del contexto CONTENIDO."""

from __future__ import annotations

from uuid import UUID

from app.contexts.content.application.commands import (
    ActualizarContenidoCommand,
    ArchivarContenidoCommand,
    BorrarContenidoCommand,
    CrearContenidoCommand,
    PublicarContenidoCommand,
    RestaurarContenidoCommand,
)
from app.contexts.content.application.dtos import ContenidoDTO, contenido_to_dto
from app.contexts.content.application.queries import ListarContenidosQuery, ObtenerContenidoQuery
from app.contexts.content.domain.model import ContentVersion, Contenido, TipoContenido
from app.contexts.content.domain.ports import (
    ContenidoRepository,
    ContentVersionRepository,
    HtmlSanitizer,
)
from app.shared.domain.base import NotFoundError, now
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


class ObtenerContenidoHandler:
    def __init__(self, repo: ContenidoRepository) -> None:
        self._repo = repo

    def handle(self, query: ObtenerContenidoQuery) -> ContenidoDTO:
        contenido = self._repo.get(query.contenido_id)
        if contenido is None or contenido.borrado:
            raise NotFoundError(f"Contenido {query.contenido_id} no encontrado.")
        return contenido_to_dto(contenido)


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

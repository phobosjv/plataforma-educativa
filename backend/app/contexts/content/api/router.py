"""Router del contexto CONTENIDO: catálogo público + gestión editor/admin."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.contexts.content.api.schemas import (
    ActualizarContenidoRequest,
    ContenidoResponse,
    CrearContenidoRequest,
)
from app.contexts.content.application.commands import (
    ActualizarContenidoCommand,
    BorrarContenidoCommand,
    CrearContenidoCommand,
    PublicarContenidoCommand,
    PurgarContenidoCommand,
    RestaurarContenidoCommand,
    SubirHtmlContenidoCommand,
)
from app.contexts.content.application.dtos import ContenidoDTO
from app.contexts.content.application.handlers import (
    ActualizarContenidoHandler,
    BorrarContenidoHandler,
    CrearContenidoHandler,
    ListarContenidosHandler,
    ObtenerContenidoHandler,
    PublicarContenidoHandler,
    PurgarContenidoHandler,
    RestaurarContenidoHandler,
    SubirHtmlContenidoHandler,
)
from app.contexts.content.application.queries import ListarContenidosQuery, ObtenerContenidoQuery
from app.contexts.content.infrastructure.html_sanitizer import Nh3HtmlSanitizer
from app.contexts.content.infrastructure.html_storage import FileSystemHtmlStorage
from app.contexts.content.infrastructure.repositories import (
    SqlAlchemyContenidoRepository,
    SqlAlchemyContentVersionRepository,
)
from app.contexts.identity.api.dependencies import require_admin, require_editor_or_admin
from app.contexts.identity.application.dtos import UsuarioDTO
from app.shared.domain.base import DomainError, NotFoundError
from app.shared.infrastructure.database import get_db
from app.shared.infrastructure.unit_of_work import UnitOfWork

router = APIRouter(tags=["content"])

# Tamaño máximo del HTML de un ejercicio interactivo (defensa contra subidas abusivas).
MAX_HTML_BYTES = 2 * 1024 * 1024


def _dto_to_response(dto: ContenidoDTO) -> ContenidoResponse:
    sandbox_url: str | None = None
    if dto.tipo == "interactivo" and dto.hash_html:
        sandbox_url = f"{settings.sandbox_base_url}/ejercicio/{dto.hash_html}"
    return ContenidoResponse(
        id=dto.id,
        titulo=dto.titulo,
        descripcion=dto.descripcion,
        tipo=dto.tipo,
        autor_id=dto.autor_id,
        publicado=dto.publicado,
        borrado=dto.borrado,
        idioma=dto.idioma,
        etiquetas=list(dto.etiquetas),
        ciclo_id=dto.ciclo_id,
        curso_id=dto.curso_id,
        asignatura_id=dto.asignatura_id,
        hash_html=dto.hash_html,
        body_html=dto.body_html,
        sandbox_url=sandbox_url,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


# --- Endpoints públicos ---


@router.get("/contenidos/", response_model=list[ContenidoResponse])
def listar_contenidos_publicos(db: Session = Depends(get_db)) -> list[ContenidoResponse]:
    repo = SqlAlchemyContenidoRepository(db)
    handler = ListarContenidosHandler(repo)
    dtos = handler.handle(ListarContenidosQuery(solo_publicados=True))
    return [_dto_to_response(d) for d in dtos]


@router.get("/contenidos/{contenido_id}", response_model=ContenidoResponse)
def obtener_contenido(contenido_id: UUID, db: Session = Depends(get_db)) -> ContenidoResponse:
    repo = SqlAlchemyContenidoRepository(db)
    handler = ObtenerContenidoHandler(repo)
    try:
        dto = handler.handle(ObtenerContenidoQuery(contenido_id=contenido_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _dto_to_response(dto)


# --- Endpoints de editor/admin ---


@router.post("/contenidos/", response_model=ContenidoResponse, status_code=status.HTTP_201_CREATED)
def crear_contenido(
    body: CrearContenidoRequest,
    current: UsuarioDTO = Depends(require_editor_or_admin),
    db: Session = Depends(get_db),
) -> ContenidoResponse:
    repo = SqlAlchemyContenidoRepository(db)
    version_repo = SqlAlchemyContentVersionRepository(db)
    uow = UnitOfWork(db)
    handler = CrearContenidoHandler(repo, version_repo, uow, Nh3HtmlSanitizer())
    try:
        uid = handler.handle(
            CrearContenidoCommand(
                titulo=body.titulo,
                descripcion=body.descripcion,
                tipo=body.tipo,
                autor_id=current.id,
                idioma=body.idioma,
                etiquetas=tuple(body.etiquetas),
                ciclo_id=body.ciclo_id,
                curso_id=body.curso_id,
                asignatura_id=body.asignatura_id,
                body_html=body.body_html,
            )
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    dto = ObtenerContenidoHandler(repo).handle(ObtenerContenidoQuery(contenido_id=uid))
    return _dto_to_response(dto)


@router.put("/contenidos/{contenido_id}", response_model=ContenidoResponse)
def actualizar_contenido(
    contenido_id: UUID,
    body: ActualizarContenidoRequest,
    current: UsuarioDTO = Depends(require_editor_or_admin),
    db: Session = Depends(get_db),
) -> ContenidoResponse:
    repo = SqlAlchemyContenidoRepository(db)
    version_repo = SqlAlchemyContentVersionRepository(db)
    uow = UnitOfWork(db)
    handler = ActualizarContenidoHandler(repo, version_repo, uow, Nh3HtmlSanitizer())
    # La taxonomía solo se reasigna si el cliente envió alguno de sus campos (así un PUT
    # parcial que no la incluye no la borra; e incluir null sí permite desasignar).
    campos = body.model_fields_set
    actualizar_taxonomia = bool(campos & {"ciclo_id", "curso_id", "asignatura_id"})
    try:
        dto = handler.handle(
            ActualizarContenidoCommand(
                contenido_id=contenido_id,
                editor_id=current.id,
                titulo=body.titulo,
                descripcion=body.descripcion,
                body_html=body.body_html,
                etiquetas=tuple(body.etiquetas) if body.etiquetas is not None else None,
                actualizar_taxonomia=actualizar_taxonomia,
                ciclo_id=body.ciclo_id,
                curso_id=body.curso_id,
                asignatura_id=body.asignatura_id,
            )
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _dto_to_response(dto)


@router.post("/contenidos/{contenido_id}/html", response_model=ContenidoResponse)
def subir_html_interactivo(
    contenido_id: UUID,
    fichero: UploadFile = File(...),
    current: UsuarioDTO = Depends(require_editor_or_admin),
    db: Session = Depends(get_db),
) -> ContenidoResponse:
    """Sube el fichero HTML de un ejercicio interactivo (NO se sanea, §10)."""
    raw_html = fichero.file.read()
    if not raw_html:
        raise HTTPException(status_code=400, detail="El fichero HTML está vacío.")
    if len(raw_html) > MAX_HTML_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"El fichero supera el máximo de {MAX_HTML_BYTES // (1024 * 1024)} MB.",
        )
    repo = SqlAlchemyContenidoRepository(db)
    version_repo = SqlAlchemyContentVersionRepository(db)
    uow = UnitOfWork(db)
    storage = FileSystemHtmlStorage(settings.media_dir)
    handler = SubirHtmlContenidoHandler(repo, version_repo, uow, storage)
    try:
        dto = handler.handle(
            SubirHtmlContenidoCommand(
                contenido_id=contenido_id, editor_id=current.id, raw_html=raw_html
            )
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _dto_to_response(dto)


@router.post("/contenidos/{contenido_id}/publicar", response_model=ContenidoResponse)
def publicar_contenido(
    contenido_id: UUID,
    current: UsuarioDTO = Depends(require_editor_or_admin),
    db: Session = Depends(get_db),
) -> ContenidoResponse:
    repo = SqlAlchemyContenidoRepository(db)
    uow = UnitOfWork(db)
    handler = PublicarContenidoHandler(repo, uow)
    try:
        dto = handler.handle(
            PublicarContenidoCommand(contenido_id=contenido_id, published_by=current.id)
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _dto_to_response(dto)


@router.delete("/contenidos/{contenido_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_contenido(
    contenido_id: UUID,
    current: UsuarioDTO = Depends(require_editor_or_admin),
    db: Session = Depends(get_db),
) -> None:
    repo = SqlAlchemyContenidoRepository(db)
    uow = UnitOfWork(db)
    handler = BorrarContenidoHandler(repo, uow)
    try:
        handler.handle(BorrarContenidoCommand(contenido_id=contenido_id, deleted_by=current.id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/contenidos/{contenido_id}/restaurar", response_model=ContenidoResponse)
def restaurar_contenido(
    contenido_id: UUID,
    current: UsuarioDTO = Depends(require_editor_or_admin),
    db: Session = Depends(get_db),
) -> ContenidoResponse:
    repo = SqlAlchemyContenidoRepository(db)
    uow = UnitOfWork(db)
    handler = RestaurarContenidoHandler(repo, uow)
    try:
        dto = handler.handle(
            RestaurarContenidoCommand(contenido_id=contenido_id, restored_by=current.id)
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _dto_to_response(dto)


# --- Endpoints de admin ---


@router.delete("/contenidos/{contenido_id}/purgar", status_code=status.HTTP_204_NO_CONTENT)
def purgar_contenido(
    contenido_id: UUID,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    """Elimina DEFINITIVAMENTE un contenido de la papelera (irreversible, solo admin)."""
    repo = SqlAlchemyContenidoRepository(db)
    uow = UnitOfWork(db)
    handler = PurgarContenidoHandler(repo, uow)
    try:
        handler.handle(PurgarContenidoCommand(contenido_id=contenido_id, purged_by=current.id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/contenidos/", response_model=list[ContenidoResponse])
def listar_todos_admin(
    _: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[ContenidoResponse]:
    repo = SqlAlchemyContenidoRepository(db)
    handler = ListarContenidosHandler(repo)
    dtos = handler.handle(ListarContenidosQuery(solo_publicados=False, incluir_borrados=True))
    return [_dto_to_response(d) for d in dtos]

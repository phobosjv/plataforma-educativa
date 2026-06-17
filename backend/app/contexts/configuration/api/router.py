from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contexts.configuration.api.schemas import (
    ActivarPaletaRequest,
    AjustesGeneralesRequest,
    ConfiguracionResponse,
    PaletaRequest,
    PaletaResponse,
)
from app.contexts.configuration.application.commands import (
    ActivarPaletaCommand,
    ActualizarAjustesGeneralesCommand,
    ActualizarPaletaCommand,
    AgregarPaletaCommand,
    EliminarPaletaCommand,
)
from app.contexts.configuration.application.handlers import (
    ActivarPaletaHandler,
    ActualizarAjustesGeneralesHandler,
    ActualizarPaletaHandler,
    AgregarPaletaHandler,
    EliminarPaletaHandler,
    ObtenerConfiguracionHandler,
)
from app.contexts.configuration.infrastructure.repositories import (
    SqlAlchemyConfiguracionRepository,
)
from app.contexts.auditing.infrastructure.recorder import registrar_auditoria
from app.contexts.identity.api.dependencies import require_admin
from app.contexts.identity.application.dtos import UsuarioDTO
from app.shared.infrastructure.database import get_db
from app.shared.infrastructure.unit_of_work import UnitOfWork

router = APIRouter(prefix="/config", tags=["configuration"])


def _auditar(
    db: Session, current: UsuarioDTO, accion: str, entidad_id: str | None = None, detalle: str = ""
) -> None:
    registrar_auditoria(
        db, usuario_id=current.id, usuario_email=current.email, usuario_rol=current.rol,
        accion=accion, entidad="configuracion", entidad_id=entidad_id, detalle=detalle,
    )


def _repo(db: Session = Depends(get_db)) -> SqlAlchemyConfiguracionRepository:
    return SqlAlchemyConfiguracionRepository(db)


def _uow(db: Session = Depends(get_db)) -> UnitOfWork:
    return UnitOfWork(db)


def _dto_to_response(dto: object) -> ConfiguracionResponse:
    from app.contexts.configuration.application.dtos import ConfiguracionDTO
    assert isinstance(dto, ConfiguracionDTO)
    return ConfiguracionResponse(
        nombre_sitio=dto.nombre_sitio,
        paleta_activa=dto.paleta_activa,
        fuente_activa=dto.fuente_activa,
        fondo_activo=dto.fondo_activo,
        fondo_estilo=dto.fondo_estilo,
        logo_url=dto.logo_url,
        aula_abierta_label=dto.aula_abierta_label,
        aula_abierta_emoji=dto.aula_abierta_emoji,
        paletas_personalizadas=[
            PaletaResponse(**p.__dict__) for p in dto.paletas_personalizadas
        ],
    )


@router.get("/", response_model=ConfiguracionResponse, summary="Obtener configuración del sitio")
def obtener_configuracion(repo: SqlAlchemyConfiguracionRepository = Depends(_repo)) -> ConfiguracionResponse:
    return _dto_to_response(ObtenerConfiguracionHandler(repo).handle())


@router.put("/general", response_model=ConfiguracionResponse,
            summary="Actualizar ajustes generales (nombre del sitio y fuente)")
def actualizar_ajustes_generales(
    body: AjustesGeneralesRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    resp = _dto_to_response(
        ActualizarAjustesGeneralesHandler(repo, uow).handle(
            ActualizarAjustesGeneralesCommand(
                nombre_sitio=body.nombre_sitio,
                fuente_activa=body.fuente_activa,
                fondo_activo=body.fondo_activo,
                fondo_estilo=body.fondo_estilo,
                logo_url=body.logo_url,
                aula_abierta_label=body.aula_abierta_label,
                aula_abierta_emoji=body.aula_abierta_emoji,
            )
        )
    )
    _auditar(db, current, "editar", detalle="ajustes generales")
    return resp


@router.put("/paleta", response_model=ConfiguracionResponse, summary="Activar paleta")
def activar_paleta(
    body: ActivarPaletaRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    resp = _dto_to_response(
        ActivarPaletaHandler(repo, uow).handle(ActivarPaletaCommand(paleta_id=body.paleta_id))
    )
    _auditar(db, current, "activar_paleta", body.paleta_id)
    return resp


@router.post("/paletas", response_model=ConfiguracionResponse, status_code=201,
             summary="Añadir paleta personalizada")
def agregar_paleta(
    body: PaletaRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    resp = _dto_to_response(
        AgregarPaletaHandler(repo, uow).handle(
            AgregarPaletaCommand(**body.model_dump())
        )
    )
    _auditar(db, current, "crear_paleta", body.id, body.nombre)
    return resp


@router.put("/paletas/{paleta_id}", response_model=ConfiguracionResponse,
            summary="Actualizar paleta personalizada")
def actualizar_paleta(
    paleta_id: str,
    body: PaletaRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    cmd = ActualizarPaletaCommand(id=paleta_id, **{k: v for k, v in body.model_dump().items() if k != "id"})
    resp = _dto_to_response(ActualizarPaletaHandler(repo, uow).handle(cmd))
    _auditar(db, current, "editar_paleta", paleta_id, body.nombre)
    return resp


@router.delete("/paletas/{paleta_id}", response_model=ConfiguracionResponse,
               summary="Eliminar paleta personalizada")
def eliminar_paleta(
    paleta_id: str,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    resp = _dto_to_response(
        EliminarPaletaHandler(repo, uow).handle(EliminarPaletaCommand(paleta_id=paleta_id))
    )
    _auditar(db, current, "borrar_paleta", paleta_id)
    return resp

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.contexts.configuration.api.schemas import (
    ActivarPaletaRequest,
    ConfiguracionResponse,
    PaletaRequest,
    PaletaResponse,
)
from app.contexts.configuration.application.commands import (
    ActivarPaletaCommand,
    ActualizarPaletaCommand,
    AgregarPaletaCommand,
    EliminarPaletaCommand,
)
from app.contexts.configuration.application.handlers import (
    ActivarPaletaHandler,
    ActualizarPaletaHandler,
    AgregarPaletaHandler,
    EliminarPaletaHandler,
    ObtenerConfiguracionHandler,
)
from app.contexts.configuration.infrastructure.repositories import (
    SqlAlchemyConfiguracionRepository,
)
from app.contexts.identity.api.dependencies import require_admin
from app.shared.infrastructure.database import get_db
from app.shared.infrastructure.unit_of_work import UnitOfWork

router = APIRouter(prefix="/config", tags=["configuration"])


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
        paletas_personalizadas=[
            PaletaResponse(**p.__dict__) for p in dto.paletas_personalizadas
        ],
    )


@router.get("/", response_model=ConfiguracionResponse, summary="Obtener configuración del sitio")
def obtener_configuracion(repo: SqlAlchemyConfiguracionRepository = Depends(_repo)) -> ConfiguracionResponse:
    return _dto_to_response(ObtenerConfiguracionHandler(repo).handle())


@router.put("/paleta", response_model=ConfiguracionResponse, summary="Activar paleta",
            dependencies=[Depends(require_admin)])
def activar_paleta(
    body: ActivarPaletaRequest,
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    return _dto_to_response(
        ActivarPaletaHandler(repo, uow).handle(ActivarPaletaCommand(paleta_id=body.paleta_id))
    )


@router.post("/paletas", response_model=ConfiguracionResponse, status_code=201,
             summary="Añadir paleta personalizada", dependencies=[Depends(require_admin)])
def agregar_paleta(
    body: PaletaRequest,
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    return _dto_to_response(
        AgregarPaletaHandler(repo, uow).handle(
            AgregarPaletaCommand(**body.model_dump())
        )
    )


@router.put("/paletas/{paleta_id}", response_model=ConfiguracionResponse,
            summary="Actualizar paleta personalizada", dependencies=[Depends(require_admin)])
def actualizar_paleta(
    paleta_id: str,
    body: PaletaRequest,
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    cmd = ActualizarPaletaCommand(id=paleta_id, **{k: v for k, v in body.model_dump().items() if k != "id"})
    return _dto_to_response(ActualizarPaletaHandler(repo, uow).handle(cmd))


@router.delete("/paletas/{paleta_id}", response_model=ConfiguracionResponse,
               summary="Eliminar paleta personalizada", dependencies=[Depends(require_admin)])
def eliminar_paleta(
    paleta_id: str,
    repo: SqlAlchemyConfiguracionRepository = Depends(_repo),
    uow: UnitOfWork = Depends(_uow),
) -> ConfiguracionResponse:
    return _dto_to_response(
        EliminarPaletaHandler(repo, uow).handle(EliminarPaletaCommand(paleta_id=paleta_id))
    )

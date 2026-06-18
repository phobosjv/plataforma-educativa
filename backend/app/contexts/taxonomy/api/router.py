"""Router del contexto TAXONOMÍA: ciclos, cursos y asignaturas."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.contexts.identity.api.dependencies import require_admin
from app.contexts.identity.application.dtos import UsuarioDTO
from app.contexts.taxonomy.api.schemas import (
    ActualizarAsignaturaRequest,
    ActualizarCicloRequest,
    ActualizarCursoRequest,
    AsignaturaResponse,
    CicloResponse,
    CrearAsignaturaRequest,
    CrearCicloRequest,
    CrearCursoRequest,
    CursoResponse,
)
from app.contexts.taxonomy.application.commands import (
    ActualizarAsignaturaCommand,
    ActualizarCicloCommand,
    ActualizarCursoCommand,
    CrearAsignaturaCommand,
    CrearCicloCommand,
    CrearCursoCommand,
    EliminarAsignaturaCommand,
    EliminarCicloCommand,
    EliminarCursoCommand,
)
from app.contexts.taxonomy.application.handlers import (
    ActualizarAsignaturaHandler,
    ActualizarCicloHandler,
    ActualizarCursoHandler,
    CrearAsignaturaHandler,
    CrearCicloHandler,
    CrearCursoHandler,
    EliminarAsignaturaHandler,
    EliminarCicloHandler,
    EliminarCursoHandler,
    ListarAsignaturasHandler,
    ListarCiclosHandler,
    ListarCursosHandler,
    ObtenerAsignaturaHandler,
    ObtenerCicloHandler,
    ObtenerCursoHandler,
)
from app.contexts.taxonomy.application.queries import (
    ListarAsignaturasQuery,
    ListarCiclosQuery,
    ListarCursosQuery,
    ObtenerAsignaturaQuery,
    ObtenerCicloQuery,
    ObtenerCursoQuery,
)
from app.contexts.taxonomy.infrastructure.repositories import (
    SqlAlchemyAsignaturaRepository,
    SqlAlchemyCicloRepository,
    SqlAlchemyCursoRepository,
)
from app.contexts.content.infrastructure.repositories import SqlAlchemyContenidoEnTaxonomia
from app.contexts.auditing.infrastructure.recorder import registrar_auditoria
from app.shared.domain.base import DomainError, NotFoundError
from app.shared.infrastructure.database import get_db
from app.shared.infrastructure.unit_of_work import UnitOfWork

router = APIRouter(prefix="/taxonomy", tags=["taxonomy"])


def _auditar(
    db: Session, current: UsuarioDTO, accion: str, entidad: str, entidad_id: str, detalle: str = ""
) -> None:
    registrar_auditoria(
        db, usuario_id=current.id, usuario_email=current.email, usuario_rol=current.rol,
        accion=accion, entidad=entidad, entidad_id=entidad_id, detalle=detalle,
    )


# ── Ciclos ────────────────────────────────────────────────────────────────────


@router.get("/ciclos/", response_model=list[CicloResponse])
def listar_ciclos(db: Session = Depends(get_db)) -> list[CicloResponse]:
    dtos = ListarCiclosHandler(SqlAlchemyCicloRepository(db)).handle(ListarCiclosQuery())
    return [CicloResponse(id=d.id, nombre=d.nombre, orden=d.orden) for d in dtos]


@router.get("/ciclos/{ciclo_id}", response_model=CicloResponse)
def obtener_ciclo(ciclo_id: UUID, db: Session = Depends(get_db)) -> CicloResponse:
    try:
        dto = ObtenerCicloHandler(SqlAlchemyCicloRepository(db)).handle(
            ObtenerCicloQuery(ciclo_id=ciclo_id)
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return CicloResponse(id=dto.id, nombre=dto.nombre, orden=dto.orden)


@router.post("/ciclos/", status_code=status.HTTP_201_CREATED)
def crear_ciclo(
    body: CrearCicloRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        uid = CrearCicloHandler(SqlAlchemyCicloRepository(db), UnitOfWork(db)).handle(
            CrearCicloCommand(nombre=body.nombre, orden=body.orden)
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    _auditar(db, current, "crear", "ciclo", str(uid), body.nombre)
    return {"id": str(uid)}


@router.put("/ciclos/{ciclo_id}", response_model=CicloResponse)
def actualizar_ciclo(
    ciclo_id: UUID,
    body: ActualizarCicloRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> CicloResponse:
    try:
        dto = ActualizarCicloHandler(SqlAlchemyCicloRepository(db), UnitOfWork(db)).handle(
            ActualizarCicloCommand(ciclo_id=ciclo_id, nombre=body.nombre, orden=body.orden)
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    _auditar(db, current, "editar", "ciclo", str(ciclo_id), dto.nombre)
    return CicloResponse(id=dto.id, nombre=dto.nombre, orden=dto.orden)


@router.delete("/ciclos/{ciclo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_ciclo(
    ciclo_id: UUID,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    try:
        EliminarCicloHandler(
            SqlAlchemyCicloRepository(db), SqlAlchemyCursoRepository(db), UnitOfWork(db)
        ).handle(EliminarCicloCommand(ciclo_id=ciclo_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=409, detail=str(e))
    _auditar(db, current, "borrar", "ciclo", str(ciclo_id))


# ── Cursos ────────────────────────────────────────────────────────────────────


@router.get("/cursos/", response_model=list[CursoResponse])
def listar_cursos(
    ciclo_id: UUID | None = None, db: Session = Depends(get_db)
) -> list[CursoResponse]:
    dtos = ListarCursosHandler(SqlAlchemyCursoRepository(db)).handle(
        ListarCursosQuery(ciclo_id=ciclo_id)
    )
    return [CursoResponse(id=d.id, nombre=d.nombre, ciclo_id=d.ciclo_id, orden=d.orden) for d in dtos]


@router.get("/cursos/{curso_id}", response_model=CursoResponse)
def obtener_curso(curso_id: UUID, db: Session = Depends(get_db)) -> CursoResponse:
    try:
        dto = ObtenerCursoHandler(SqlAlchemyCursoRepository(db)).handle(
            ObtenerCursoQuery(curso_id=curso_id)
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return CursoResponse(id=dto.id, nombre=dto.nombre, ciclo_id=dto.ciclo_id, orden=dto.orden)


@router.post("/cursos/", status_code=status.HTTP_201_CREATED)
def crear_curso(
    body: CrearCursoRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        uid = CrearCursoHandler(
            SqlAlchemyCursoRepository(db), SqlAlchemyCicloRepository(db), UnitOfWork(db)
        ).handle(CrearCursoCommand(nombre=body.nombre, ciclo_id=body.ciclo_id, orden=body.orden))
    except (NotFoundError, DomainError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    _auditar(db, current, "crear", "curso", str(uid), body.nombre)
    return {"id": str(uid)}


@router.put("/cursos/{curso_id}", response_model=CursoResponse)
def actualizar_curso(
    curso_id: UUID,
    body: ActualizarCursoRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> CursoResponse:
    try:
        dto = ActualizarCursoHandler(SqlAlchemyCursoRepository(db), UnitOfWork(db)).handle(
            ActualizarCursoCommand(curso_id=curso_id, nombre=body.nombre, orden=body.orden)
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    _auditar(db, current, "editar", "curso", str(curso_id), dto.nombre)
    return CursoResponse(id=dto.id, nombre=dto.nombre, ciclo_id=dto.ciclo_id, orden=dto.orden)


@router.delete("/cursos/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_curso(
    curso_id: UUID,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    try:
        EliminarCursoHandler(
            SqlAlchemyCursoRepository(db), SqlAlchemyContenidoEnTaxonomia(db), UnitOfWork(db)
        ).handle(EliminarCursoCommand(curso_id=curso_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=409, detail=str(e))
    _auditar(db, current, "borrar", "curso", str(curso_id))


# ── Asignaturas ───────────────────────────────────────────────────────────────


@router.get("/asignaturas/", response_model=list[AsignaturaResponse])
def listar_asignaturas(db: Session = Depends(get_db)) -> list[AsignaturaResponse]:
    dtos = ListarAsignaturasHandler(SqlAlchemyAsignaturaRepository(db)).handle(
        ListarAsignaturasQuery()
    )
    return [
        AsignaturaResponse(id=d.id, nombre=d.nombre, color=d.color, transversal=d.transversal)
        for d in dtos
    ]


@router.get("/asignaturas/{asignatura_id}", response_model=AsignaturaResponse)
def obtener_asignatura(asignatura_id: UUID, db: Session = Depends(get_db)) -> AsignaturaResponse:
    try:
        dto = ObtenerAsignaturaHandler(SqlAlchemyAsignaturaRepository(db)).handle(
            ObtenerAsignaturaQuery(asignatura_id=asignatura_id)
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return AsignaturaResponse(
        id=dto.id, nombre=dto.nombre, color=dto.color, transversal=dto.transversal
    )


@router.post("/asignaturas/", status_code=status.HTTP_201_CREATED)
def crear_asignatura(
    body: CrearAsignaturaRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    try:
        uid = CrearAsignaturaHandler(SqlAlchemyAsignaturaRepository(db), UnitOfWork(db)).handle(
            CrearAsignaturaCommand(
                nombre=body.nombre, color=body.color, transversal=body.transversal
            )
        )
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    _auditar(db, current, "crear", "asignatura", str(uid), body.nombre)
    return {"id": str(uid)}


@router.put("/asignaturas/{asignatura_id}", response_model=AsignaturaResponse)
def actualizar_asignatura(
    asignatura_id: UUID,
    body: ActualizarAsignaturaRequest,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AsignaturaResponse:
    try:
        dto = ActualizarAsignaturaHandler(
            SqlAlchemyAsignaturaRepository(db), UnitOfWork(db)
        ).handle(
            ActualizarAsignaturaCommand(
                asignatura_id=asignatura_id,
                nombre=body.nombre,
                color=body.color,
                transversal=body.transversal,
            )
        )
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))
    _auditar(db, current, "editar", "asignatura", str(asignatura_id), dto.nombre)
    return AsignaturaResponse(
        id=dto.id, nombre=dto.nombre, color=dto.color, transversal=dto.transversal
    )


@router.delete("/asignaturas/{asignatura_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_asignatura(
    asignatura_id: UUID,
    current: UsuarioDTO = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    try:
        EliminarAsignaturaHandler(
            SqlAlchemyAsignaturaRepository(db), SqlAlchemyContenidoEnTaxonomia(db), UnitOfWork(db)
        ).handle(EliminarAsignaturaCommand(asignatura_id=asignatura_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DomainError as e:
        raise HTTPException(status_code=409, detail=str(e))
    _auditar(db, current, "borrar", "asignatura", str(asignatura_id))

"""Integridad referencial a nivel de BD (PRAGMA foreign_keys=ON + FKs de content).

Verifica que SQLite hace cumplir las claves foráneas cuando la conexión las activa (como hace
``database.py`` en la app). Los demás tests usan engines sin ese PRAGMA, por eso aquí se crea
uno propio que sí lo activa.
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime, timezone

import pytest
from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

import app.bootstrap  # noqa: F401 — registra los modelos ORM
from app.shared.infrastructure.database import Base


@pytest.fixture()
def engine_fk() -> Generator[Engine, None, None]:
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(eng, "connect")
    def _fk(dbapi_conn: object, _: object) -> None:
        cur = dbapi_conn.cursor()  # type: ignore[union-attr]
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(eng)
    try:
        yield eng
    finally:
        eng.dispose()


def _insertar_curso_con_contenido(conn: object) -> None:
    ahora = datetime.now(timezone.utc).isoformat()
    conn.execute(text("INSERT INTO ciclo (id, nombre, orden) VALUES ('ci', 'Ciclo', 0)"))
    conn.execute(
        text("INSERT INTO curso (id, nombre, ciclo_id, orden) VALUES ('cu', '1', 'ci', 0)")
    )
    conn.execute(
        text(
            "INSERT INTO content (id, tipo, titulo, descripcion, idioma, is_published, "
            "is_deleted, is_exam, curso_id, tags_json, created_at, updated_at) VALUES "
            "('co', 'texto', 'Ficha', '', 'es', 0, 0, 0, 'cu', '[]', :t, :t)"
        ),
        {"t": ahora},
    )


def test_no_se_puede_borrar_curso_referenciado(engine_fk: Engine) -> None:
    with engine_fk.begin() as conn:
        _insertar_curso_con_contenido(conn)
    # Borrar el curso referenciado por un contenido debe fallar (ON DELETE RESTRICT).
    with pytest.raises(IntegrityError):
        with engine_fk.begin() as conn:
            conn.execute(text("DELETE FROM curso WHERE id = 'cu'"))


def test_se_puede_borrar_curso_sin_referencias(engine_fk: Engine) -> None:
    with engine_fk.begin() as conn:
        _insertar_curso_con_contenido(conn)
        # Si primero se quita el contenido, el curso ya puede borrarse.
        conn.execute(text("DELETE FROM content WHERE id = 'co'"))
        conn.execute(text("DELETE FROM curso WHERE id = 'cu'"))
    with engine_fk.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM curso")).scalar() == 0


def test_no_se_puede_insertar_contenido_con_curso_inexistente(engine_fk: Engine) -> None:
    ahora = datetime.now(timezone.utc).isoformat()
    with pytest.raises(IntegrityError):
        with engine_fk.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO content (id, tipo, titulo, descripcion, idioma, is_published, "
                    "is_deleted, is_exam, curso_id, tags_json, created_at, updated_at) VALUES "
                    "('x', 'texto', 'T', '', 'es', 0, 0, 0, 'fantasma', '[]', :t, :t)"
                ),
                {"t": ahora},
            )

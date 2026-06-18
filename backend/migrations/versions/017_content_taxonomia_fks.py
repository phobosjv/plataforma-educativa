"""Añade claves foráneas (ON DELETE RESTRICT) de content a la taxonomía.

Hace cumplir a nivel de BD que ``content.ciclo_id/curso_id/asignatura_id`` apunten a una
taxonomía existente (refuerza la guarda de dominio). SQLite no permite ``ALTER`` para añadir
una FK: hay que recrear la tabla (batch). Como el índice FTS5 ``content_fts`` es de *contenido
externo* sobre ``content`` (mapea por ``rowid``, que cambia al recrear), se suelta antes y se
reconstruye después.

La migración corre con las claves foráneas desactivadas (es el modo por defecto de la conexión
de Alembic), así que la recreación de la tabla no tropieza con las referencias existentes.

Revision ID: 017
Revises: 016
Create Date: 2026-06-18
"""

from __future__ import annotations

from alembic import op

from app.contexts.content.infrastructure.fts import (
    crear_indice_busqueda,
    eliminar_indice_busqueda,
)

revision = "017"
down_revision = "016"
branch_labels = None
depends_on = None


def _dbapi():
    return op.get_bind().connection.dbapi_connection


def upgrade() -> None:
    eliminar_indice_busqueda(_dbapi())
    with op.batch_alter_table("content", schema=None) as batch:
        batch.create_foreign_key(
            "fk_content_ciclo", "ciclo", ["ciclo_id"], ["id"], ondelete="RESTRICT"
        )
        batch.create_foreign_key(
            "fk_content_curso", "curso", ["curso_id"], ["id"], ondelete="RESTRICT"
        )
        batch.create_foreign_key(
            "fk_content_asignatura", "asignatura", ["asignatura_id"], ["id"], ondelete="RESTRICT"
        )
    crear_indice_busqueda(_dbapi())


def downgrade() -> None:
    eliminar_indice_busqueda(_dbapi())
    with op.batch_alter_table("content", schema=None) as batch:
        batch.drop_constraint("fk_content_asignatura", type_="foreignkey")
        batch.drop_constraint("fk_content_curso", type_="foreignkey")
        batch.drop_constraint("fk_content_ciclo", type_="foreignkey")
    crear_indice_busqueda(_dbapi())

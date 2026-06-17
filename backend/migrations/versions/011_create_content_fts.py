"""Crea el índice de búsqueda full-text content_fts (FTS5) y sus triggers.

Tabla virtual FTS5 de contenido externo sobre ``content`` (titulo, descripcion,
tags_json), con tokenizador que ignora acentos, mantenida por triggers. El DDL vive
en ``app.contexts.content.infrastructure.fts`` para no duplicarlo entre la migración
y los tests. Ver CLAUDE.md §8 (búsqueda mediante FTS5).

Revision ID: 011
Revises: 010
Create Date: 2026-06-17
"""

from __future__ import annotations

from alembic import op

from app.contexts.content.infrastructure.fts import (
    crear_indice_busqueda,
    eliminar_indice_busqueda,
)

revision = "011"
down_revision = "010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabla virtual + triggers se crean sobre la conexión SQLite cruda (FTS5 es DDL
    # de SQLite, no del dialecto de SQLAlchemy). 'rebuild' indexa lo ya existente.
    crear_indice_busqueda(op.get_bind().connection.dbapi_connection)


def downgrade() -> None:
    eliminar_indice_busqueda(op.get_bind().connection.dbapi_connection)

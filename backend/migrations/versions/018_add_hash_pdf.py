"""Añade hash_pdf a content y content_version.

Tercer tipo de contenido: ficha PDF imprimible. El fichero PDF se guarda content-addressed
(SHA-256, inmutable) y se referencia por hash, igual que el HTML de los ejercicios interactivos
(``hash_html``). La columna también se versiona en ``content_version`` para que restaurar una
versión recupere el PDF que tenía en ese momento.

Es un simple ADD COLUMN nullable: no afecta al índice FTS5 ``content_fts`` (de contenido externo
sobre ``content``), que solo referencia titulo/descripcion/tags_json por nombre y mapea por rowid;
añadir una columna no cambia los rowids ni las columnas indexadas, así que no hace falta el baile
de soltar/reconstruir el índice.

Revision ID: 018
Revises: 017
Create Date: 2026-06-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "018"
down_revision = "017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("content", sa.Column("hash_pdf", sa.String(), nullable=True))
    op.add_column("content_version", sa.Column("hash_pdf", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("content_version", "hash_pdf")
    op.drop_column("content", "hash_pdf")

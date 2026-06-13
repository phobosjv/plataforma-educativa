"""Añade la columna fuente_activa a site_config.

Permite seleccionar la tipografía del sitio entre un catálogo de fuentes
self-hosted (ver contexto configuration). Por defecto "sistema".

Revision ID: 005
Revises: 004
Create Date: 2026-06-14
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_config",
        sa.Column(
            "fuente_activa",
            sa.String(100),
            nullable=False,
            server_default="sistema",
        ),
    )


def downgrade() -> None:
    op.drop_column("site_config", "fuente_activa")

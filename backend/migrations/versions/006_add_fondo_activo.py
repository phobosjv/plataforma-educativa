"""Añade la columna fondo_activo a site_config.

Permite seleccionar un fondo/estampado temático del sitio entre un catálogo de
patrones SVG self-hosted. Por defecto "ninguno" (fondo liso).

Revision ID: 006
Revises: 005
Create Date: 2026-06-14
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_config",
        sa.Column(
            "fondo_activo",
            sa.String(100),
            nullable=False,
            server_default="ninguno",
        ),
    )


def downgrade() -> None:
    op.drop_column("site_config", "fondo_activo")

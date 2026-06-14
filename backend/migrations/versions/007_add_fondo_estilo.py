"""Añade la columna fondo_estilo a site_config.

Permite elegir la disposición del estampado: "ordenado" (tile fijo repetido) o
"desordenado" (patrón disperso sin dos iconos iguales adyacentes). Por defecto "ordenado".

Revision ID: 007
Revises: 006
Create Date: 2026-06-14
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_config",
        sa.Column(
            "fondo_estilo",
            sa.String(100),
            nullable=False,
            server_default="ordenado",
        ),
    )


def downgrade() -> None:
    op.drop_column("site_config", "fondo_estilo")

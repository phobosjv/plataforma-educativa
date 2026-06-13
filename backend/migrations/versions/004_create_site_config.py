"""Crea la tabla site_config para ConfiguracionSitio (singleton).

Revision ID: 004
Revises: 003
Create Date: 2026-06-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "site_config",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("nombre_sitio", sa.String(255), nullable=False, server_default="Plataforma Educativa"),
        sa.Column("paleta_activa", sa.String(100), nullable=False, server_default="cielo"),
        sa.Column("paletas_json", sa.Text, nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_table("site_config")

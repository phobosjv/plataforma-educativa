"""Añade logo_url a site_config.

URL relativa (servida por el propio origen, /media/images/...) del logotipo del sitio,
o cadena vacía si no hay logo. El logo se muestra junto al nombre en la cabecera.

Revision ID: 010
Revises: 009
Create Date: 2026-06-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "010"
down_revision = "009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_config",
        sa.Column("logo_url", sa.String(500), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("site_config", "logo_url")

"""Añade mostrar_version a site_config.

Controla si el badge de versión (cms-version) se muestra junto al nombre del sitio
en PublicLayout y AdminLayout. El valor por defecto es True (visible) para mantener
retrocompatibilidad con instalaciones existentes.

Revision ID: 019
Revises: 018
Create Date: 2026-06-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "019"
down_revision = "018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_config",
        sa.Column("mostrar_version", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column("site_config", "mostrar_version")

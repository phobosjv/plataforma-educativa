"""Añade redes_sociales_json a site_config (enlaces a redes sociales del pie público).

Revision ID: 015
Revises: 014
Create Date: 2026-06-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "015"
down_revision = "014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_config",
        sa.Column("redes_sociales_json", sa.Text(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("site_config", "redes_sociales_json")

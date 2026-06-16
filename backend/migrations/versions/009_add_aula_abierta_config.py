"""Añade aula_abierta_label y aula_abierta_emoji a site_config.

Etiqueta y emoji configurables de la entrada a las asignaturas transversales en el catálogo
("Aula Abierta" por defecto). Cada centro elige el término que prefiera.

Revision ID: 009
Revises: 008
Create Date: 2026-06-16
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "009"
down_revision = "008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_config",
        sa.Column("aula_abierta_label", sa.String(40), nullable=False, server_default="Aula Abierta"),
    )
    op.add_column(
        "site_config",
        sa.Column("aula_abierta_emoji", sa.String(16), nullable=False, server_default="🌟"),
    )


def downgrade() -> None:
    op.drop_column("site_config", "aula_abierta_emoji")
    op.drop_column("site_config", "aula_abierta_label")

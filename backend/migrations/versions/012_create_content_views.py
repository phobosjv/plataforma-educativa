"""Crea content_views: total agregado de visitas por contenido.

El contador de visitas se agrega en memoria y se vuelca por lotes a esta tabla
(CLAUDE.md §8). Visitas anónimas y agregadas (§10): solo un total por contenido.

Revision ID: 012
Revises: 011
Create Date: 2026-06-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "012"
down_revision = "011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_views",
        sa.Column("content_id", sa.String(), primary_key=True),
        sa.Column("total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("content_views")

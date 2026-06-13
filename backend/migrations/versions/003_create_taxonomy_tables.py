"""Crea las tablas ciclo, curso y asignatura (contexto taxonomy).

Revision ID: 003
Revises: 002
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ciclo",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "curso",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("ciclo_id", sa.String(), sa.ForeignKey("ciclo.id"), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_table(
        "asignatura",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("color", sa.String(), nullable=False, server_default="#6366f1"),
    )


def downgrade() -> None:
    op.drop_table("curso")
    op.drop_table("ciclo")
    op.drop_table("asignatura")

"""Crea audit_log: registro de acciones de gestión (auditoría).

Append-only: quién hizo qué, sobre qué objeto y cuándo (CLAUDE.md §3, §5). Solo lectura
para admin desde la API; no se edita ni se borra desde la aplicación.

Revision ID: 013
Revises: 012
Create Date: 2026-06-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_log",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("usuario_id", sa.String(), nullable=True),
        sa.Column("usuario_email", sa.String(), nullable=False, server_default=""),
        sa.Column("usuario_rol", sa.String(), nullable=False, server_default=""),
        sa.Column("accion", sa.String(), nullable=False),
        sa.Column("entidad", sa.String(), nullable=False),
        sa.Column("entidad_id", sa.String(), nullable=True),
        sa.Column("detalle", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_audit_log_created_at", "audit_log", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_audit_log_created_at", table_name="audit_log")
    op.drop_table("audit_log")

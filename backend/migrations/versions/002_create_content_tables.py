"""Crea las tablas content y content_version (contexto content).

Revision ID: 002
Revises: 001
Create Date: 2026-06-13
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tipo", sa.String(), nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("descripcion", sa.String(), nullable=False, server_default=""),
        sa.Column("autor_id", sa.String(), nullable=True),
        sa.Column("ciclo_id", sa.String(), nullable=True),
        sa.Column("curso_id", sa.String(), nullable=True),
        sa.Column("asignatura_id", sa.String(), nullable=True),
        sa.Column("idioma", sa.String(), nullable=False, server_default="es"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("hash_html", sa.String(), nullable=True),
        sa.Column("body_html", sa.Text(), nullable=True),
        sa.Column("tags_json", sa.String(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "content_version",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("content_id", sa.String(), sa.ForeignKey("content.id"), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("metadata_snapshot_json", sa.Text(), nullable=False),
        sa.Column("body_html", sa.Text(), nullable=True),
        sa.Column("hash_html", sa.String(), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_id", "version_no"),
    )
    op.create_index("ix_content_version_content_id", "content_version", ["content_id"])


def downgrade() -> None:
    op.drop_index("ix_content_version_content_id", table_name="content_version")
    op.drop_table("content_version")
    op.drop_table("content")

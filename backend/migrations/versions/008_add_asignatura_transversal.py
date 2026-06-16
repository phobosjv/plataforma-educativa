"""Añade la columna is_transversal a asignatura.

Marca las asignaturas transversales (p. ej. Audición y Lenguaje, Pedagogía Terapéutica),
cuyo contenido se agrupa en "Aula Abierta" en vez de por ciclo/curso. Por defecto False.

Revision ID: 008
Revises: 007
Create Date: 2026-06-16
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "asignatura",
        sa.Column(
            "is_transversal",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("asignatura", "is_transversal")

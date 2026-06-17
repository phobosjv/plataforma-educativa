"""Añade a site_config: textos del catálogo, donaciones y publicidad.

- catalogo_titulo / catalogo_subtitulo: textos configurables de la pantalla inicial del
  catálogo (dirigibles a los padres si hay publicidad).
- donaciones_json: lista de enlaces de donación (PayPal y otras plataformas).
- publicidad_activa / publicidad_html_izquierda / publicidad_html_derecha: anuncios en los
  márgenes de las pantallas públicas de navegación (zona de adultos, §10).

Revision ID: 014
Revises: 013
Create Date: 2026-06-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "014"
down_revision = "013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "site_config",
        sa.Column(
            "catalogo_titulo", sa.String(120), nullable=False, server_default="¿En qué curso estás?"
        ),
    )
    op.add_column(
        "site_config",
        sa.Column(
            "catalogo_subtitulo",
            sa.String(120),
            nullable=False,
            server_default="Toca tu curso para ver las actividades",
        ),
    )
    op.add_column(
        "site_config",
        sa.Column("donaciones_json", sa.Text(), nullable=False, server_default="[]"),
    )
    op.add_column(
        "site_config",
        sa.Column(
            "publicidad_activa", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "site_config",
        sa.Column("publicidad_html_izquierda", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "site_config",
        sa.Column("publicidad_html_derecha", sa.Text(), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("site_config", "publicidad_html_derecha")
    op.drop_column("site_config", "publicidad_html_izquierda")
    op.drop_column("site_config", "publicidad_activa")
    op.drop_column("site_config", "donaciones_json")
    op.drop_column("site_config", "catalogo_subtitulo")
    op.drop_column("site_config", "catalogo_titulo")

"""Add str_value column to site_settings.

Revision ID: 0003_add_str_value_to_site_settings
Revises: 0002_add_price_unit_type_to_supplier_services
Create Date: 2026-03-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_add_str_value_to_site_settings"
down_revision = "0002_add_price_unit_type_to_supplier_services"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("site_settings", sa.Column("str_value", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("site_settings", "str_value")


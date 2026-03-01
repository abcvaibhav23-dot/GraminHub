"""Add price_unit_type to supplier_services (v1).

Revision ID: 0002_add_price_unit_type_to_supplier_services
Revises: 0001_add_v2_core_tables
Create Date: 2026-03-01
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_add_price_unit_type_to_supplier_services"
down_revision = "0001_add_v2_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "supplier_services",
        sa.Column("price_unit_type", sa.String(length=40), nullable=False, server_default="per_item"),
    )
    op.alter_column("supplier_services", "price_unit_type", server_default=None)


def downgrade() -> None:
    op.drop_column("supplier_services", "price_unit_type")


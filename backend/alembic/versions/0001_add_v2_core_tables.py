"""Add v2 core tables (suppliers + bookings).

Revision ID: 0001_add_v2_core_tables
Revises: 
Create Date: 2026-02-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_add_v2_core_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "v2_suppliers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("business_name", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("address", sa.String(length=300), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("reviewer_user_id", sa.Integer(), nullable=True),
        sa.Column("status_updated_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_v2_suppliers_tenant_owner", "v2_suppliers", ["tenant_id", "owner_user_id"])
    op.create_index("ix_v2_suppliers_tenant_status", "v2_suppliers", ["tenant_id", "status"])

    op.create_table(
        "v2_supplier_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("supplier_id", sa.Integer(), sa.ForeignKey("v2_suppliers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doc_type", sa.String(length=50), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_v2_supplier_documents_tenant_supplier",
        "v2_supplier_documents",
        ["tenant_id", "supplier_id"],
    )
    op.create_index("ix_v2_supplier_documents_tenant_status", "v2_supplier_documents", ["tenant_id", "status"])

    op.create_table(
        "v2_bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("buyer_user_id", sa.Integer(), nullable=False),
        sa.Column("supplier_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_v2_bookings_tenant_buyer", "v2_bookings", ["tenant_id", "buyer_user_id"])
    op.create_index("ix_v2_bookings_tenant_supplier", "v2_bookings", ["tenant_id", "supplier_id"])
    op.create_index("ix_v2_bookings_tenant_status", "v2_bookings", ["tenant_id", "status"])

    op.create_table(
        "v2_booking_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("booking_id", sa.Integer(), sa.ForeignKey("v2_bookings.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("from_state", sa.String(length=40), nullable=True),
        sa.Column("to_state", sa.String(length=40), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_v2_booking_events_tenant_booking",
        "v2_booking_events",
        ["tenant_id", "booking_id"],
    )
    op.create_index("ix_v2_booking_events_tenant_created", "v2_booking_events", ["tenant_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_v2_booking_events_tenant_created", table_name="v2_booking_events")
    op.drop_index("ix_v2_booking_events_tenant_booking", table_name="v2_booking_events")
    op.drop_table("v2_booking_events")

    op.drop_index("ix_v2_bookings_tenant_status", table_name="v2_bookings")
    op.drop_index("ix_v2_bookings_tenant_supplier", table_name="v2_bookings")
    op.drop_index("ix_v2_bookings_tenant_buyer", table_name="v2_bookings")
    op.drop_table("v2_bookings")

    op.drop_index("ix_v2_supplier_documents_tenant_status", table_name="v2_supplier_documents")
    op.drop_index("ix_v2_supplier_documents_tenant_supplier", table_name="v2_supplier_documents")
    op.drop_table("v2_supplier_documents")

    op.drop_index("ix_v2_suppliers_tenant_status", table_name="v2_suppliers")
    op.drop_index("ix_v2_suppliers_tenant_owner", table_name="v2_suppliers")
    op.drop_table("v2_suppliers")


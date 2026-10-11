"""Add durable payment notification events and idempotency keys.

Revision ID: c7b3e8f1a204
Revises: f2a8c5d1e904
Create Date: 2026-08-14 16:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "c7b3e8f1a204"
down_revision: Union[str, Sequence[str], None] = "a9c3e7d5b102"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "payment_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False, server_default="alipay"),
        sa.Column("event_key", sa.String(length=128), nullable=False),
        sa.Column("dedupe_key", sa.String(length=64), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_no", sa.String(length=32), nullable=False),
        sa.Column("trade_no", sa.String(length=100), nullable=False),
        sa.Column("notification_id", sa.String(length=128), nullable=True),
        sa.Column("trade_status", sa.String(length=32), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("processing_result", sa.String(length=32), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "event_key", name="uq_payment_events_provider_event_key"),
        sa.UniqueConstraint("provider", "dedupe_key", name="uq_payment_events_provider_dedupe_key"),
    )
    op.create_index("idx_payment_events_order_id", "payment_events", ["order_id"])
    op.create_index("idx_payment_events_trade_no", "payment_events", ["provider", "trade_no"])
    op.create_index("ix_payment_events_order_no", "payment_events", ["order_no"])
    op.create_index("ix_payment_events_trade_no", "payment_events", ["trade_no"])


def downgrade() -> None:
    op.drop_index("ix_payment_events_trade_no", table_name="payment_events")
    op.drop_index("ix_payment_events_order_no", table_name="payment_events")
    op.drop_index("idx_payment_events_trade_no", table_name="payment_events")
    op.drop_index("idx_payment_events_order_id", table_name="payment_events")
    op.drop_table("payment_events")

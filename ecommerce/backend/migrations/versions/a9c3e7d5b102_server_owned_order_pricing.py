"""Add idempotency and versioned order snapshot references.

Revision ID: a9c3e7d5b102
Revises: b7e1c4a9d203
Create Date: 2026-08-10 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a9c3e7d5b102"
down_revision: Union[str, Sequence[str], None] = "b7e1c4a9d203"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("idempotency_key", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("orders", sa.Column("request_fingerprint", sa.String(length=64), nullable=True))
    op.create_unique_constraint(
        "uq_orders_user_idempotency_key",
        "orders",
        ["user_id", "idempotency_key"],
    )
    op.add_column("order_items", sa.Column("configuration_id", sa.String(length=100), nullable=True))
    op.add_column("order_items", sa.Column("configuration_version", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("order_items", "configuration_version")
    op.drop_column("order_items", "configuration_id")
    op.drop_constraint("uq_orders_user_idempotency_key", "orders", type_="unique")
    op.drop_column("orders", "request_fingerprint")
    op.drop_column("orders", "idempotency_key")

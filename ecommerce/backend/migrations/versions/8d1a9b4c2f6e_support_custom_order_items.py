"""Support custom order items

Revision ID: 8d1a9b4c2f6e
Revises: ad260c2f895d
Create Date: 2026-05-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "8d1a9b4c2f6e"
down_revision: Union[str, Sequence[str], None] = "ad260c2f895d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "order_items",
        sa.Column("item_type", sa.String(20), nullable=False, server_default="product"),
    )
    op.add_column("order_items", sa.Column("product_specs", postgresql.JSONB(), nullable=True))
    op.alter_column("order_items", "product_id", nullable=True)
    op.alter_column("order_items", "item_type", server_default=None)


def downgrade() -> None:
    op.alter_column("order_items", "product_id", nullable=False)
    op.drop_column("order_items", "product_specs")
    op.drop_column("order_items", "item_type")

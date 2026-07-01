"""Support custom order items

Revision ID: 8d1a9b4c2f6e
Revises: ad260c2f895d
Create Date: 2026-05-31 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = "8d1a9b4c2f6e"
down_revision: Union[str, Sequence[str], None] = "ad260c2f895d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Some installations were initialized from database/init.sql, while the
    # original initial Alembic revision already contains these columns. Keep
    # this compatibility migration safe for both histories and offline SQL.
    op.execute("""
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'order_items' AND column_name = 'item_type'
          ) THEN
            ALTER TABLE order_items ADD COLUMN item_type VARCHAR(20) NOT NULL DEFAULT 'product';
            ALTER TABLE order_items ALTER COLUMN item_type DROP DEFAULT;
          END IF;

          IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'order_items' AND column_name = 'product_specs'
          ) THEN
            ALTER TABLE order_items ADD COLUMN product_specs JSONB;
          END IF;

          ALTER TABLE order_items ALTER COLUMN product_id DROP NOT NULL;
        END $$;
    """)


def downgrade() -> None:
    # This revision may have been a no-op when the initial schema supplied the
    # columns, so a destructive downgrade cannot safely infer ownership.
    pass

"""Fix Supabase security and foreign-key advisor findings.

Revision ID: f2a8c5d1e904
Revises: e6f4a1b9c207
Create Date: 2026-06-23 03:30:00.000000
"""
from typing import Sequence, Union

from alembic import op


revision: str = "f2a8c5d1e904"
down_revision: Union[str, Sequence[str], None] = "e6f4a1b9c207"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS extensions")
    op.execute("ALTER EXTENSION pg_trgm SET SCHEMA extensions")
    op.execute("ALTER FUNCTION public.update_updated_at_column() SET search_path = public, pg_temp")
    op.execute("CREATE INDEX IF NOT EXISTS idx_cart_product_id ON cart_items (product_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_price_history_changed_by ON price_history (changed_by)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_price_history_changed_by")
    op.execute("DROP INDEX IF EXISTS idx_cart_product_id")
    op.execute("ALTER FUNCTION public.update_updated_at_column() RESET search_path")
    op.execute("ALTER EXTENSION pg_trgm SET SCHEMA public")

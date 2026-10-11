"""Keep SQL-seeded categories visible after an Alembic-only installation.

Revision ID: d9b4e6a2c301
Revises: c7b3e8f1a204
"""
from alembic import op
import sqlalchemy as sa

revision = "d9b4e6a2c301"
down_revision = "c7b3e8f1a204"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Python-side defaults do not apply to seed.sql or external SQL imports.
    op.alter_column("categories", "is_active", server_default=sa.true())
    op.alter_column("categories", "sort_order", server_default="0")
    op.execute("UPDATE categories SET is_active = true WHERE is_active IS NULL")
    op.execute("UPDATE categories SET sort_order = 0 WHERE sort_order IS NULL")


def downgrade() -> None:
    op.alter_column("categories", "is_active", server_default=None)
    op.alter_column("categories", "sort_order", server_default=None)

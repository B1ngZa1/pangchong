"""Add catalog asset source provenance.

Revision ID: b7e1c4a9d203
Revises: f2a8c5d1e904
Create Date: 2026-07-01 00:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "b7e1c4a9d203"
down_revision: Union[str, Sequence[str], None] = "f2a8c5d1e904"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("asset_source_url", sa.String(500)))


def downgrade() -> None:
    op.drop_column("products", "asset_source_url")

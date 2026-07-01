"""Add catalog asset metadata and auditable price provenance.

Revision ID: c4b7e2a9d130
Revises: 8d1a9b4c2f6e
Create Date: 2026-06-23 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c4b7e2a9d130"
down_revision: Union[str, Sequence[str], None] = "8d1a9b4c2f6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("model_3d_url", sa.String(500)))
    op.add_column("products", sa.Column("model_3d_scale", sa.Numeric(8, 4), nullable=False, server_default="1"))
    op.add_column("products", sa.Column("model_3d_position", postgresql.JSONB()))
    op.add_column("products", sa.Column("model_3d_rotation", postgresql.JSONB()))
    op.add_column("products", sa.Column("asset_license", sa.String(100)))
    op.add_column("products", sa.Column("price_source_name", sa.String(100)))
    op.add_column("products", sa.Column("price_source_url", sa.String(500)))
    op.add_column("products", sa.Column("price_checked_at", sa.DateTime(timezone=True)))
    op.add_column("price_history", sa.Column("source_name", sa.String(100)))
    op.add_column("price_history", sa.Column("source_url", sa.String(500)))
    op.execute("CREATE INDEX IF NOT EXISTS idx_price_history_created_at ON price_history (created_at)")

    # Supabase's public schema can be exposed by the Data API. The application
    # uses only trusted SQLAlchemy connections, so browser roles get no grants.
    op.execute("""
        DO $$
        DECLARE role_name text;
        BEGIN
          FOREACH role_name IN ARRAY ARRAY['anon', 'authenticated'] LOOP
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name) THEN
              EXECUTE format('REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM %I', role_name);
              EXECUTE format('REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM %I', role_name);
              EXECUTE format('REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA public FROM %I', role_name);
              EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM %I', role_name);
              EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM %I', role_name);
              EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE EXECUTE ON FUNCTIONS FROM %I', role_name);
            END IF;
          END LOOP;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
          IF to_regclass('storage.buckets') IS NOT NULL THEN
            INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
            VALUES
              ('catalog-images', 'catalog-images', true, 5242880, ARRAY['image/png', 'image/jpeg', 'image/webp']),
              ('catalog-models', 'catalog-models', true, 20971520, ARRAY['model/gltf-binary', 'application/octet-stream'])
            ON CONFLICT (id) DO UPDATE SET
              public = EXCLUDED.public,
              file_size_limit = EXCLUDED.file_size_limit,
              allowed_mime_types = EXCLUDED.allowed_mime_types;
          END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_price_history_created_at")
    op.drop_column("price_history", "source_url")
    op.drop_column("price_history", "source_name")
    op.drop_column("products", "price_checked_at")
    op.drop_column("products", "price_source_url")
    op.drop_column("products", "price_source_name")
    op.drop_column("products", "asset_license")
    op.drop_column("products", "model_3d_rotation")
    op.drop_column("products", "model_3d_position")
    op.drop_column("products", "model_3d_scale")
    op.drop_column("products", "model_3d_url")

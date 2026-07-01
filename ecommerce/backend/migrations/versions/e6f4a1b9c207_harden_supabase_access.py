"""Harden Supabase API access and catalog storage.

Revision ID: e6f4a1b9c207
Revises: c4b7e2a9d130
Create Date: 2026-06-23 03:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


revision: str = "e6f4a1b9c207"
down_revision: Union[str, Sequence[str], None] = "c4b7e2a9d130"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Automatic RLS setup may create this SECURITY DEFINER function in public.
    # The application does not expose database RPCs to browser roles.
    op.execute("""
        DO $$
        BEGIN
          IF to_regprocedure('public.rls_auto_enable()') IS NOT NULL THEN
            REVOKE ALL ON FUNCTION public.rls_auto_enable() FROM PUBLIC;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
              REVOKE ALL ON FUNCTION public.rls_auto_enable() FROM anon;
            END IF;
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
              REVOKE ALL ON FUNCTION public.rls_auto_enable() FROM authenticated;
            END IF;
          END IF;
        END $$;
    """)
    op.execute("""
        DO $$
        BEGIN
          IF to_regclass('storage.buckets') IS NOT NULL THEN
            INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
            VALUES
              ('catalog-images', 'catalog-images', true, 5242880,
               ARRAY['image/png', 'image/jpeg', 'image/webp']),
              ('catalog-models', 'catalog-models', true, 20971520,
               ARRAY['model/gltf-binary', 'application/octet-stream'])
            ON CONFLICT (id) DO UPDATE SET
              public = EXCLUDED.public,
              file_size_limit = EXCLUDED.file_size_limit,
              allowed_mime_types = EXCLUDED.allowed_mime_types;
          END IF;
        END $$;
    """)


def downgrade() -> None:
    # Do not restore public execution or delete user assets on downgrade.
    pass

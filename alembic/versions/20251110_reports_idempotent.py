"""Reports and financial tables - idempotent migration

Revision ID: 20251110_reports_idempotent
Revises: 20251110_reports
Create Date: 2025-11-10

This migration is a no-op because the tables were already created by
SQLAlchemy's Base.metadata.create_all() during app initialization.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20251110_reports_idempotent"
down_revision = "20251110_reports"
branch_labels = None
depends_on = None


def upgrade():
    # Tables already exist from app initialization, so this is a no-op
    pass


def downgrade():
    # No-op for downgrade too
    pass

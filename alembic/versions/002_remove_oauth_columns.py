"""Drop social OAuth columns from users table

Revision ID: 002_remove_oauth_columns
Revises: 001_initial
Create Date: 2025-11-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_remove_oauth_columns'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop social-related columns that were removed from the SQLAlchemy model
    with op.batch_alter_table('users') as batch_op:
        # safe-drop if column exists (some DBs will error if not present)
        try:
            batch_op.drop_column('profile_picture_url')
        except Exception:
            pass
        try:
            batch_op.drop_column('oauth_provider')
        except Exception:
            pass
        try:
            batch_op.drop_column('oauth_provider_id')
        except Exception:
            pass


def downgrade() -> None:
    # Re-create the columns if downgrading
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('profile_picture_url', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('oauth_provider', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('oauth_provider_id', sa.String(), nullable=True))

"""
Add availability column to rooms table
"""
# Alembic identifiers
revision = '20251120_add_availability_to_rooms'
down_revision = '20251110_reports_idempotent'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('rooms', sa.Column('availability', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('rooms', 'availability')

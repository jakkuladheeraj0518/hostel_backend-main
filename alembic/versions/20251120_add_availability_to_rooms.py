"""
Add availability column to rooms table
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('rooms', sa.Column('availability', sa.Integer(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('rooms', 'availability')

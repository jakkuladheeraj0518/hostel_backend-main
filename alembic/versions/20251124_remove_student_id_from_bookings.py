"""
Remove student_id column from bookings table

Revision ID: 20251124_remove_student_id_from_bookings
Revises: 20251120_add_availability_to_rooms
Create Date: 2025-11-24
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251124_remove_student_id_from_bookings'
down_revision = '20251120_add_availability_to_rooms'
branch_labels = None
depends_on = None

def upgrade():
    op.drop_column('bookings', 'student_id')

def downgrade():
    op.add_column('bookings', sa.Column('student_id', sa.String(), nullable=True))

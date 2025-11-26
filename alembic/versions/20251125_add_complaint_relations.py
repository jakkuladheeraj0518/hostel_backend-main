"""add complaint relations

Revision ID: 20251125_add_complaint_relations
Revises: 
Create Date: 2025-11-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20251125_add_complaint_relations'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if columns already exist before adding
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('complaints')]
    
    if 'student_id' not in columns:
        op.add_column('complaints', sa.Column('student_id', sa.String(), nullable=True))
        op.create_index(op.f('ix_complaints_student_id'), 'complaints', ['student_id'], unique=False)
        op.create_foreign_key('fk_complaints_student', 'complaints', 'students', ['student_id'], ['student_id'], ondelete='SET NULL')

    if 'reporter_id' not in columns:
        op.add_column('complaints', sa.Column('reporter_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_complaints_reporter_id'), 'complaints', ['reporter_id'], unique=False)
        op.create_foreign_key('fk_complaints_reporter', 'complaints', 'users', ['reporter_id'], ['id'], ondelete='SET NULL')

    if 'assigned_to_id' not in columns:
        op.add_column('complaints', sa.Column('assigned_to_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_complaints_assigned_to_id'), 'complaints', ['assigned_to_id'], unique=False)
        op.create_foreign_key('fk_complaints_assigned_to', 'complaints', 'users', ['assigned_to_id'], ['id'], ondelete='SET NULL')

    if 'hostel_id' not in columns:
        op.add_column('complaints', sa.Column('hostel_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_complaints_hostel_id'), 'complaints', ['hostel_id'], unique=False)
        op.create_foreign_key('fk_complaints_hostel', 'complaints', 'hostels', ['hostel_id'], ['id'], ondelete='SET NULL')

    if 'room_id' not in columns:
        op.add_column('complaints', sa.Column('room_id', sa.Integer(), nullable=True))
        op.create_index(op.f('ix_complaints_room_id'), 'complaints', ['room_id'], unique=False)
        op.create_foreign_key('fk_complaints_room', 'complaints', 'rooms', ['room_id'], ['id'], ondelete='SET NULL')

    # Make denormalized fields nullable
    try:
        op.alter_column('complaints', 'student_name', existing_type=sa.String(255), nullable=True)
    except Exception:
        pass
    try:
        op.alter_column('complaints', 'student_email', existing_type=sa.String(255), nullable=True)
    except Exception:
        pass
    try:
        op.alter_column('complaints', 'hostel_name', existing_type=sa.String(255), nullable=True)
    except Exception:
        pass


def downgrade() -> None:
    # Drop FK constraints
    try:
        op.drop_constraint('fk_complaints_room', 'complaints', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_constraint('fk_complaints_hostel', 'complaints', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_constraint('fk_complaints_assigned_to', 'complaints', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_constraint('fk_complaints_reporter', 'complaints', type_='foreignkey')
    except Exception:
        pass
    try:
        op.drop_constraint('fk_complaints_student', 'complaints', type_='foreignkey')
    except Exception:
        pass

    # Drop indexes
    try:
        op.drop_index(op.f('ix_complaints_room_id'), table_name='complaints')
    except Exception:
        pass
    try:
        op.drop_index(op.f('ix_complaints_hostel_id'), table_name='complaints')
    except Exception:
        pass
    try:
        op.drop_index(op.f('ix_complaints_assigned_to_id'), table_name='complaints')
    except Exception:
        pass
    try:
        op.drop_index(op.f('ix_complaints_reporter_id'), table_name='complaints')
    except Exception:
        pass
    try:
        op.drop_index(op.f('ix_complaints_student_id'), table_name='complaints')
    except Exception:
        pass

    # Drop columns
    try:
        op.drop_column('complaints', 'room_id')
    except Exception:
        pass
    try:
        op.drop_column('complaints', 'hostel_id')
    except Exception:
        pass
    try:
        op.drop_column('complaints', 'assigned_to_id')
    except Exception:
        pass
    try:
        op.drop_column('complaints', 'reporter_id')
    except Exception:
        pass
    try:
        op.drop_column('complaints', 'student_id')
    except Exception:
        pass

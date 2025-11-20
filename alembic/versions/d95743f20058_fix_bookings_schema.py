"""fix bookings schema

Revision ID: d95743f20058
Revises: 003
Create Date: 2025-11-17 22:17:46.009382
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd95743f20058'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # ---- FIX: CREATE bookings table without recreating ENUM ----
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('visitor_id', sa.Integer(), nullable=False),
        sa.Column('hostel_id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('check_in', sa.DateTime(), nullable=False),
        sa.Column('check_out', sa.DateTime(), nullable=False),
        sa.Column('amount_paid', sa.Float(), nullable=True),

        # ---- FIX: use existing PostgreSQL ENUM, NOT SQLAlchemy Enum ----
        sa.Column(
            'status',
            postgresql.ENUM(
                'pending', 'confirmed', 'cancelled', 'rejected',
                name='bookingstatus',
                create_type=False  # <---- IMPORTANT FIX
            ),
            server_default='pending',
            nullable=False
        ),

        sa.Column('created_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['hostel_id'], ['hostels.id']),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)

    # rooms table adjustments
    op.alter_column('rooms', 'total_beds',
               existing_type=sa.INTEGER(),
               server_default=None,
               existing_nullable=False)

    op.alter_column('rooms', 'available_beds',
               existing_type=sa.INTEGER(),
               server_default=None,
               existing_nullable=False)

    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)

    op.create_foreign_key(None, 'rooms', 'hostels', ['hostel_id'], ['id'])

    op.alter_column('waitlist', 'priority',
               existing_type=sa.INTEGER(),
               server_default=None,
               nullable=True)

    op.alter_column('waitlist', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)


def downgrade():
    op.alter_column('waitlist', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)

    op.alter_column('waitlist', 'priority',
               existing_type=sa.INTEGER(),
               server_default=sa.text('1'),
               nullable=False)

    op.drop_constraint(None, 'rooms', type_='foreignkey')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')

    op.alter_column('rooms', 'available_beds',
               existing_type=sa.INTEGER(),
               server_default=sa.text('1'),
               existing_nullable=False)

    op.alter_column('rooms', 'total_beds',
               existing_type=sa.INTEGER(),
               server_default=sa.text('1'),
               existing_nullable=False)

    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_table('bookings')

    # no visitors table recreation

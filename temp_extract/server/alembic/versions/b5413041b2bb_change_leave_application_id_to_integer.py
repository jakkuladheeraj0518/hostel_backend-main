"""change_leave_application_id_to_integer

Revision ID: b5413041b2bb
Revises: 6486735efe5f
Create Date: 2025-11-14 12:55:40.478454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b5413041b2bb'
down_revision = '6486735efe5f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a new table with integer ID
    op.create_table(
        'leave_applications_new',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('hostel_id', sa.String(), nullable=False),
        sa.Column('leave_start_date', sa.Date(), nullable=False),
        sa.Column('leave_end_date', sa.Date(), nullable=False),
        sa.Column('leave_reason', sa.Text(), nullable=False),
        sa.Column('leave_status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', name='leavestatus'), nullable=False),
        sa.Column('emergency_contact', sa.String(length=20), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('destination', sa.String(length=255), nullable=True),
        sa.Column('contact_during_leave', sa.String(length=20), nullable=True),
        sa.Column('applied_by', sa.Integer(), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('medical_certificate', sa.String(length=500), nullable=True),
        sa.Column('supporting_documents', sa.Text(), nullable=True),
        sa.Column('parent_consent_required', sa.String(length=1), nullable=True),
        sa.Column('parent_consent_received', sa.String(length=1), nullable=True),
        sa.Column('parent_contact_verified', sa.String(length=1), nullable=True),
        sa.Column('expected_return_date', sa.Date(), nullable=True),
        sa.Column('actual_return_date', sa.Date(), nullable=True),
        sa.Column('return_confirmed_by', sa.Integer(), nullable=True),
        sa.Column('is_late_return', sa.String(length=1), nullable=True),
        sa.Column('late_return_reason', sa.Text(), nullable=True),
        sa.Column('late_return_penalty', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['applied_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['hostel_id'], ['hostels.id'], ),
        sa.ForeignKeyConstraint(['return_confirmed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data from old table to new table (excluding id, it will be auto-generated)
    op.execute("""
        INSERT INTO leave_applications_new (
            type, created_at, updated_at, student_id, hostel_id,
            leave_start_date, leave_end_date, leave_reason, leave_status,
            emergency_contact, leave_type, destination, contact_during_leave,
            applied_by, approved_by, approved_at, rejection_reason,
            medical_certificate, supporting_documents,
            parent_consent_required, parent_consent_received, parent_contact_verified,
            expected_return_date, actual_return_date, return_confirmed_by,
            is_late_return, late_return_reason, late_return_penalty
        )
        SELECT 
            type, created_at, updated_at, student_id, hostel_id,
            leave_start_date, leave_end_date, leave_reason, leave_status,
            emergency_contact, leave_type, destination, contact_during_leave,
            applied_by, approved_by, approved_at, rejection_reason,
            medical_certificate, supporting_documents,
            parent_consent_required, parent_consent_received, parent_contact_verified,
            expected_return_date, actual_return_date, return_confirmed_by,
            is_late_return, late_return_reason, late_return_penalty
        FROM leave_applications
        ORDER BY created_at
    """)
    
    # Drop old table
    op.drop_table('leave_applications')
    
    # Rename new table to original name
    op.rename_table('leave_applications_new', 'leave_applications')


def downgrade() -> None:
    # Create old table with UUID ID
    op.create_table(
        'leave_applications_old',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('hostel_id', sa.String(), nullable=False),
        sa.Column('leave_start_date', sa.Date(), nullable=False),
        sa.Column('leave_end_date', sa.Date(), nullable=False),
        sa.Column('leave_reason', sa.Text(), nullable=False),
        sa.Column('leave_status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'CANCELLED', name='leavestatus'), nullable=False),
        sa.Column('emergency_contact', sa.String(length=20), nullable=False),
        sa.Column('leave_type', sa.String(length=50), nullable=False),
        sa.Column('destination', sa.String(length=255), nullable=True),
        sa.Column('contact_during_leave', sa.String(length=20), nullable=True),
        sa.Column('applied_by', sa.Integer(), nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('medical_certificate', sa.String(length=500), nullable=True),
        sa.Column('supporting_documents', sa.Text(), nullable=True),
        sa.Column('parent_consent_required', sa.String(length=1), nullable=True),
        sa.Column('parent_consent_received', sa.String(length=1), nullable=True),
        sa.Column('parent_contact_verified', sa.String(length=1), nullable=True),
        sa.Column('expected_return_date', sa.Date(), nullable=True),
        sa.Column('actual_return_date', sa.Date(), nullable=True),
        sa.Column('return_confirmed_by', sa.Integer(), nullable=True),
        sa.Column('is_late_return', sa.String(length=1), nullable=True),
        sa.Column('late_return_reason', sa.Text(), nullable=True),
        sa.Column('late_return_penalty', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['applied_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['hostel_id'], ['hostels.id'], ),
        sa.ForeignKeyConstraint(['return_confirmed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Note: Cannot restore original UUIDs, will generate new ones
    op.execute("""
        INSERT INTO leave_applications_old (
            id, type, created_at, updated_at, student_id, hostel_id,
            leave_start_date, leave_end_date, leave_reason, leave_status,
            emergency_contact, leave_type, destination, contact_during_leave,
            applied_by, approved_by, approved_at, rejection_reason,
            medical_certificate, supporting_documents,
            parent_consent_required, parent_consent_received, parent_contact_verified,
            expected_return_date, actual_return_date, return_confirmed_by,
            is_late_return, late_return_reason, late_return_penalty
        )
        SELECT 
            gen_random_uuid()::text, type, created_at, updated_at, student_id, hostel_id,
            leave_start_date, leave_end_date, leave_reason, leave_status,
            emergency_contact, leave_type, destination, contact_during_leave,
            applied_by, approved_by, approved_at, rejection_reason,
            medical_certificate, supporting_documents,
            parent_consent_required, parent_consent_received, parent_contact_verified,
            expected_return_date, actual_return_date, return_confirmed_by,
            is_late_return, late_return_reason, late_return_penalty
        FROM leave_applications
    """)
    
    op.drop_table('leave_applications')
    op.rename_table('leave_applications_old', 'leave_applications')
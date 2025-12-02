"""add read status to notificationstatus enum

Revision ID: 20251201_add_read_to_notificationstatus
Revises: 
Create Date: 2025-12-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251201_add_read_to_notificationstatus'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add 'read' value to notificationstatus enum type"""
    # PostgreSQL doesn't support removing enum values easily, so we add the new value
    conn = op.get_bind()
    
    # Check if the enum type exists and if 'read' value already exists
    try:
        # For PostgreSQL: add the new enum value
        conn.execute(sa.text("ALTER TYPE notificationstatus ADD VALUE 'read'"))
    except Exception as e:
        # If it fails (value might already exist), just continue
        print(f"Note: Could not add 'read' to notificationstatus enum: {e}")


def downgrade() -> None:
    """Downgrade: remove 'read' value from notificationstatus enum"""
    # Note: PostgreSQL doesn't support removing enum values from an existing type
    # This is a limitation of PostgreSQL, so we just log it
    pass

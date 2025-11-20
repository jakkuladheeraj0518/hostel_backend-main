"""create waitlist table"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "waitlist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("hostel_id", sa.Integer(), nullable=False),
        sa.Column("room_type", sa.String(), nullable=False),
        sa.Column("visitor_id", sa.Integer(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table("waitlist")

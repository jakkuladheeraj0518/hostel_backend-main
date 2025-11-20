"""create rooms table"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "001"
down_revision = "000"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("hostel_id", sa.Integer(), nullable=False),
        sa.Column("room_type", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("total_beds", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("available_beds", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade():
    op.drop_table("rooms")

"""create bookings table"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    # Create ENUM only once
    op.execute(
        "CREATE TYPE bookingstatus AS ENUM ('pending', 'confirmed', 'cancelled', 'rejected');"
    )

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("hostel_id", sa.Integer, sa.ForeignKey("hostels.id")),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id")),
        sa.Column("visitor_name", sa.String(255), nullable=False),
        sa.Column("visitor_email", sa.String(255), nullable=False),
        sa.Column("check_in_date", sa.Date, nullable=False),
        sa.Column("check_out_date", sa.Date, nullable=False),

        sa.Column(
            "status",
            postgresql.ENUM(
                "pending", "confirmed", "cancelled", "rejected",
                name="bookingstatus",
                create_type=False
            ),
            server_default="pending",
            nullable=False,
        ),

        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("bookings")
    op.execute("DROP TYPE IF EXISTS bookingstatus CASCADE;")

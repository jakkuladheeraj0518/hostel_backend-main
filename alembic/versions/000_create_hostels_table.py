"""create hostels table"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "hostels",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(), nullable=True),
        sa.Column("pincode", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("gender_type", sa.String(), nullable=True),
        sa.Column("amenities", sa.Text(), nullable=True),
    )


def downgrade():
    op.drop_table("hostels")

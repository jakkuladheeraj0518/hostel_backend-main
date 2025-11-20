from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as psql

# revision identifiers, used by Alembic.
revision = "20251110_reports"
down_revision = "20251107_admin_permissions"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()

    # create Postgres enum types explicitly — check if they already exist first
    # Using IF NOT EXISTS pattern via dialect-specific checks
    from sqlalchemy import inspect
    inspector = inspect(bind)
    existing_types = {t['name'] for t in inspector.get_enums()}
    existing_tables = set(inspector.get_table_names())

    if 'bookingstatus' not in existing_types:
        psql.ENUM('pending','confirmed','completed','cancelled', name='bookingstatus').create(bind, checkfirst=True)
    if 'paymentstatus' not in existing_types:
        psql.ENUM('pending','paid','failed','refunded', name='paymentstatus').create(bind, checkfirst=True)
    if 'commissionstatus' not in existing_types:
        psql.ENUM('pending','paid','processing', name='commissionstatus').create(bind, checkfirst=True)
    if 'reporttype' not in existing_types:
        psql.ENUM('revenue','commission','booking','user_activity','subscription','system_performance', name='reporttype').create(bind, checkfirst=True)
    if 'exportformat' not in existing_types:
        psql.ENUM('pdf','csv','excel', name='exportformat').create(bind, checkfirst=True)

    if "bookings" not in existing_tables:
        op.create_table(
            "bookings",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("hostel_id", sa.String(), nullable=False),
            sa.Column("hostel_name", sa.String(), nullable=False),
            sa.Column("user_id", sa.String(), nullable=False),
            sa.Column("user_name", sa.String(), nullable=False),
            sa.Column("room_type", sa.String(), nullable=False),
            sa.Column("check_in_date", sa.DateTime(), nullable=False),
            sa.Column("check_out_date", sa.DateTime(), nullable=False),
            sa.Column("amount", sa.Numeric(10, 2), nullable=False),
            sa.Column("commission_rate", sa.Numeric(5, 4), nullable=False),
            sa.Column("commission_amount", sa.Numeric(10, 2), nullable=False),
            sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("payment_status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        )

    if "commissions" not in existing_tables:
        op.create_table(
            "commissions",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("booking_id", sa.String(), sa.ForeignKey("bookings.id"), nullable=False, unique=True),
            sa.Column("amount", sa.Numeric(10, 2), nullable=False),
            sa.Column("status", sa.String(), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("earned_date", sa.DateTime(), nullable=False),
            sa.Column("paid_date", sa.DateTime(), nullable=True),
            sa.Column("hostel_id", sa.String(), nullable=False),
            sa.Column("platform_revenue", sa.Numeric(10, 2), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        )

    if "subscription_revenues" not in existing_tables:
        op.create_table(
            "subscription_revenues",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("subscription_id", sa.String(), nullable=False),
            sa.Column("organization_id", sa.String(), nullable=False),
            sa.Column("organization_name", sa.String(), nullable=False),
            sa.Column("amount", sa.Numeric(10, 2), nullable=False),
            sa.Column("plan_name", sa.String(), nullable=False),
            sa.Column("billing_date", sa.DateTime(), nullable=False),
            sa.Column("period_start", sa.DateTime(), nullable=False),
            sa.Column("period_end", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        )

    if "reports" not in existing_tables:
        op.create_table(
            "reports",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("report_type", sa.String(), nullable=False),
            sa.Column("start_date", sa.DateTime(), nullable=False),
            sa.Column("end_date", sa.DateTime(), nullable=False),
            sa.Column("parameters", sa.JSON(), nullable=True),
            sa.Column("result_data", sa.JSON(), nullable=True),
            sa.Column("file_path", sa.String(), nullable=True),
            sa.Column("export_format", sa.String(), nullable=True),
            sa.Column("generated_by", sa.String(), nullable=False),
            sa.Column("generated_at", sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column("is_automated", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("is_scheduled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        )

    if "financial_summaries" not in existing_tables:
        op.create_table(
            "financial_summaries",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("period_start", sa.DateTime(), nullable=False),
            sa.Column("period_end", sa.DateTime(), nullable=False),
            sa.Column("total_income", sa.Numeric(10, 2), server_default=sa.text('0'), nullable=False),
            sa.Column("subscription_revenue", sa.Numeric(10, 2), server_default=sa.text('0'), nullable=False),
            sa.Column("commission_earned", sa.Numeric(10, 2), server_default=sa.text('0'), nullable=False),
            sa.Column("pending_payments", sa.Numeric(10, 2), server_default=sa.text('0'), nullable=False),
            sa.Column("total_bookings", sa.Integer(), server_default=sa.text('0'), nullable=False),
            sa.Column("completed_bookings", sa.Integer(), server_default=sa.text('0'), nullable=False),
            sa.Column("cancelled_bookings", sa.Integer(), server_default=sa.text('0'), nullable=False),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column("updated_at", sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        )


def downgrade():
    op.drop_table("financial_summaries")
    op.drop_table("reports")
    op.drop_table("subscription_revenues")
    op.drop_table("commissions")
    op.drop_table("bookings")

    bind = op.get_bind()
    psql.ENUM('pdf','csv','excel', name='exportformat').drop(bind, checkfirst=True)
    psql.ENUM('revenue','commission','booking','user_activity','subscription','system_performance', name='reporttype').drop(bind, checkfirst=True)
    psql.ENUM('pending','paid','processing', name='commissionstatus').drop(bind, checkfirst=True)
    psql.ENUM('pending','paid','failed','refunded', name='paymentstatus').drop(bind, checkfirst=True)
    psql.ENUM('pending','confirmed','completed','cancelled', name='bookingstatus').drop(bind, checkfirst=True)
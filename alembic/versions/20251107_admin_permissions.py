"""Add admin permissions and hostel assignments

Revision ID: 20251107_admin_permissions
Revises: 20251105_hostels_dashboard
Create Date: 2025-11-07

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '20251107_admin_permissions'
down_revision = '20251105_hostels_dashboard'
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing type if exists
    op.execute("DROP TYPE IF EXISTS permission_level CASCADE")
    
    # Create enum type
    op.execute("CREATE TYPE permission_level AS ENUM ('read', 'write', 'admin')")
    
    # Create assignments table
    op.execute("""
    CREATE TABLE IF NOT EXISTS admin_hostel_assignments (
        id SERIAL PRIMARY KEY,
        admin_id INT NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
        hostel_id INT NOT NULL REFERENCES hostels(id) ON DELETE CASCADE,
        permission_level permission_level NOT NULL DEFAULT 'read',
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(admin_id, hostel_id)
    );

    CREATE INDEX IF NOT EXISTS idx_admin_hostel_assignments_admin_id 
        ON admin_hostel_assignments(admin_id);
    CREATE INDEX IF NOT EXISTS idx_admin_hostel_assignments_hostel_id 
        ON admin_hostel_assignments(hostel_id);

    -- Function to assign admin to multiple hostels
    CREATE OR REPLACE FUNCTION bulk_assign_admin_to_hostels(
        p_admin_id INT,
        p_hostel_ids INT[],
        p_permission_level permission_level DEFAULT 'read'
    ) RETURNS SETOF admin_hostel_assignments AS $$
    DECLARE
        hostel_id INT;
        assignment admin_hostel_assignments;
    BEGIN
        FOREACH hostel_id IN ARRAY p_hostel_ids LOOP
            INSERT INTO admin_hostel_assignments (admin_id, hostel_id, permission_level)
            VALUES (p_admin_id, hostel_id, p_permission_level)
            ON CONFLICT (admin_id, hostel_id) 
            DO UPDATE SET permission_level = p_permission_level
            RETURNING * INTO assignment;
            RETURN NEXT assignment;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;
    """)

def downgrade():
    op.execute("""
    DROP FUNCTION IF EXISTS bulk_assign_admin_to_hostels() CASCADE;
    DROP TABLE IF EXISTS admin_hostel_assignments CASCADE;
    DROP TYPE IF EXISTS permission_level CASCADE;
    """)
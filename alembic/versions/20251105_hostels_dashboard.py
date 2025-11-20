from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic.
revision = '20251105_hostels_dashboard'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================================
    # ✅ TABLE CREATION
    # =========================================================================
    op.execute("""
    CREATE EXTENSION IF NOT EXISTS pg_trgm;

    CREATE TABLE IF NOT EXISTS locations (
        id SERIAL PRIMARY KEY,
        city TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS hostels (
        id SERIAL PRIMARY KEY,
        hostel_name TEXT NOT NULL,
        description TEXT,
        full_address TEXT,
        hostel_type TEXT,
        contact_email TEXT,
        contact_phone TEXT,
        amenities TEXT,
        rules TEXT,
        check_in TIME,
        check_out TIME,
        total_beds INT,
        current_occupancy INT,
        monthly_revenue NUMERIC(12,2),
        visibility TEXT DEFAULT 'public',
        is_featured BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        location_id INT REFERENCES locations(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        admin_name TEXT NOT NULL,
        email TEXT UNIQUE,
        is_active BOOLEAN DEFAULT TRUE,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS revenues (
        id SERIAL PRIMARY KEY,
        hostel_id INT NOT NULL REFERENCES hostels(id) ON DELETE CASCADE,
        month DATE NOT NULL,
        revenue NUMERIC(12,2) NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(hostel_id, month)
    );

    CREATE TABLE IF NOT EXISTS occupancies (
        id SERIAL PRIMARY KEY,
        hostel_id INT NOT NULL REFERENCES hostels(id) ON DELETE CASCADE,
        month DATE NOT NULL,
        occupancy_rate NUMERIC(5,2) NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(hostel_id, month)
    );

    CREATE TABLE IF NOT EXISTS activities (
        id SERIAL PRIMARY KEY,
        entity_name TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        action TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_hostels_location_id ON hostels(location_id);
    CREATE INDEX IF NOT EXISTS idx_hostels_created_at ON hostels(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_hostels_is_featured ON hostels(is_featured) WHERE is_featured = TRUE;
    CREATE INDEX IF NOT EXISTS idx_hostels_visibility ON hostels(visibility);
    CREATE INDEX IF NOT EXISTS idx_hostels_name_trgm ON hostels USING gin(hostel_name gin_trgm_ops);
    CREATE INDEX IF NOT EXISTS idx_revenues_hostel_month ON revenues(hostel_id, month DESC);
    CREATE INDEX IF NOT EXISTS idx_revenues_month ON revenues(month DESC);
    CREATE INDEX IF NOT EXISTS idx_occupancies_hostel_month ON occupancies(hostel_id, month DESC);
    CREATE INDEX IF NOT EXISTS idx_occupancies_month ON occupancies(month DESC);
    CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_activities_entity_type ON activities(entity_type);
    CREATE INDEX IF NOT EXISTS idx_admins_is_active ON admins(is_active) WHERE is_active = TRUE;
    """)

    # =========================================================================
    # ✅ CONSTRAINTS
    # =========================================================================
    constraints_sql = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_occupancy_not_exceed_beds') THEN
            ALTER TABLE hostels ADD CONSTRAINT chk_occupancy_not_exceed_beds
            CHECK (current_occupancy IS NULL OR total_beds IS NULL OR current_occupancy <= total_beds);
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_total_beds_positive') THEN
            ALTER TABLE hostels ADD CONSTRAINT chk_total_beds_positive
            CHECK (total_beds IS NULL OR total_beds >= 0);
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_current_occupancy_positive') THEN
            ALTER TABLE hostels ADD CONSTRAINT chk_current_occupancy_positive
            CHECK (current_occupancy IS NULL OR current_occupancy >= 0);
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_monthly_revenue_positive') THEN
            ALTER TABLE hostels ADD CONSTRAINT chk_monthly_revenue_positive
            CHECK (monthly_revenue IS NULL OR monthly_revenue >= 0);
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_visibility_values') THEN
            ALTER TABLE hostels ADD CONSTRAINT chk_visibility_values
            CHECK (visibility IN ('public', 'private'));
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_revenue_positive') THEN
            ALTER TABLE revenues ADD CONSTRAINT chk_revenue_positive
            CHECK (revenue >= 0);
        END IF;

        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_occupancy_rate_range') THEN
            ALTER TABLE occupancies ADD CONSTRAINT chk_occupancy_rate_range
            CHECK (occupancy_rate >= 0 AND occupancy_rate <= 100);
        END IF;
    END $$;
    """
    op.execute(constraints_sql)

    # =========================================================================
    # ✅ FUNCTIONS / STORED PROCEDURES
    # =========================================================================
    op.execute("""
CREATE OR REPLACE FUNCTION public.upsert_hostel(
    p_id integer,
    p_hostel_name character varying,
    p_description text,
    p_full_address text,
    p_hostel_type character varying,
    p_contact_email character varying,
    p_contact_phone character varying,
    p_amenities text,
    p_rules text,
    p_check_in time without time zone,
    p_check_out time without time zone,
    p_total_beds integer,
    p_current_occupancy integer,
    p_monthly_revenue numeric,
    p_visibility character varying DEFAULT 'public'::character varying,
    p_is_featured boolean DEFAULT false,
    p_location_id integer DEFAULT NULL::integer)
RETURNS TABLE(
    id integer,
    hostel_name character varying,
    description text,
    full_address text,
    hostel_type character varying,
    contact_email character varying,
    contact_phone character varying,
    amenities text,
    rules text,
    check_in time without time zone,
    check_out time without time zone,
    total_beds integer,
    current_occupancy integer,
    monthly_revenue numeric,
    visibility character varying,
    is_featured boolean,
    created_at timestamp without time zone,
    location_id integer)
LANGUAGE plpgsql
AS $BODY$
BEGIN
    IF p_id IS NOT NULL AND EXISTS (SELECT 1 FROM hostels WHERE hostels.id = p_id) THEN
        UPDATE hostels SET
            hostel_name = p_hostel_name,
            description = p_description,
            full_address = p_full_address,
            hostel_type = p_hostel_type,
            contact_email = p_contact_email,
            contact_phone = p_contact_phone,
            amenities = p_amenities,
            rules = p_rules,
            check_in = p_check_in,
            check_out = p_check_out,
            total_beds = p_total_beds,
            current_occupancy = p_current_occupancy,
            monthly_revenue = p_monthly_revenue,
            visibility = p_visibility,
            is_featured = p_is_featured,
            location_id = p_location_id
        WHERE hostels.id = p_id;

        RETURN QUERY
        SELECT 
            hostels.id, hostels.hostel_name, hostels.description, hostels.full_address, hostels.hostel_type,
            hostels.contact_email, hostels.contact_phone, hostels.amenities, hostels.rules, hostels.check_in, hostels.check_out,
            hostels.total_beds, hostels.current_occupancy, hostels.monthly_revenue, hostels.visibility, hostels.is_featured,
            hostels.created_at, hostels.location_id
        FROM hostels WHERE hostels.id = p_id;

    ELSE
        RETURN QUERY
        INSERT INTO hostels (
            hostel_name, description, full_address, hostel_type, contact_email,
            contact_phone, amenities, rules, check_in, check_out, total_beds,
            current_occupancy, monthly_revenue, visibility, is_featured, location_id
        ) VALUES (
            p_hostel_name, p_description, p_full_address, p_hostel_type,
            p_contact_email, p_contact_phone, p_amenities, p_rules, p_check_in,
            p_check_out, p_total_beds, p_current_occupancy, p_monthly_revenue,
            p_visibility, p_is_featured, p_location_id
        )
        RETURNING
            hostels.id, hostels.hostel_name, hostels.description, hostels.full_address, hostels.hostel_type,
            hostels.contact_email, hostels.contact_phone, hostels.amenities, hostels.rules, hostels.check_in, hostels.check_out,
            hostels.total_beds, hostels.current_occupancy, hostels.monthly_revenue, hostels.visibility, hostels.is_featured,
            hostels.created_at, hostels.location_id;
    END IF;
END;
$BODY$;


    CREATE OR REPLACE FUNCTION get_dashboard_and_activities()
    RETURNS JSON LANGUAGE plpgsql AS $$
    DECLARE
        summary JSON;
        recent JSON;
    BEGIN
        SELECT json_build_object(
            'total_hostels', (SELECT COUNT(*) FROM hostels),
            'active_admins', (SELECT COUNT(*) FROM admins WHERE is_active = TRUE),
            'monthly_revenue', COALESCE((SELECT SUM(revenue)
                FROM revenues WHERE date_trunc('month', month) = date_trunc('month', current_date)), 0),
            'avg_occupancy', COALESCE((SELECT ROUND(AVG(occupancy_rate), 2)
                FROM occupancies WHERE date_trunc('month', month) = date_trunc('month', current_date)), 0)
        ) INTO summary;

        SELECT json_agg(json_build_object(
            'entity_name', entity_name,
            'entity_type', entity_type,
            'action', action,
            'created_at', to_char(created_at, 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
        )) INTO recent
        FROM (SELECT * FROM activities ORDER BY created_at DESC LIMIT 10) sub;

        RETURN json_build_object('summary', summary, 'recent_activities', COALESCE(recent, '[]'::json));
    END;
    $$;

    CREATE OR REPLACE FUNCTION get_top_performing_hostels()
    RETURNS TABLE (rank INT, hostel_name VARCHAR(255), city VARCHAR(100), revenue NUMERIC, occupancy NUMERIC)
    LANGUAGE plpgsql AS $$
    BEGIN
        RETURN QUERY
        SELECT
            CAST(ROW_NUMBER() OVER (ORDER BY COALESCE(SUM(r.revenue), 0) DESC) AS INT) AS rank,
            h.hostel_name::VARCHAR(255),
            COALESCE(l.city, 'Unknown')::VARCHAR(100) AS city,
            COALESCE(SUM(r.revenue), 0) AS revenue,
            COALESCE(ROUND(AVG(o.occupancy_rate), 2), 0) AS occupancy
        FROM hostels h
        LEFT JOIN locations l ON l.id = h.location_id
        LEFT JOIN revenues r ON r.hostel_id = h.id
            AND date_trunc('month', r.month) = date_trunc('month', current_date)
        LEFT JOIN occupancies o ON o.hostel_id = h.id
            AND date_trunc('month', o.month) = date_trunc('month', current_date)
        GROUP BY h.hostel_name, l.city
        ORDER BY revenue DESC
        LIMIT 5;
    END;
    $$;

    -- ✅ Added Function: get_hostel_occupancy_and_revenue
    CREATE OR REPLACE FUNCTION get_hostel_occupancy_and_revenue(p_hostel_id INT)
    RETURNS TABLE (
        occupancy_rate NUMERIC,
        revenue NUMERIC
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            o.occupancy_rate,
            r.revenue
        FROM 
            public.occupancies o
        FULL JOIN 
            public.revenues r 
        ON o.hostel_id = r.hostel_id
        WHERE 
            o.hostel_id = p_hostel_id OR r.hostel_id = p_hostel_id;
    END;
    $$;
    """)


def downgrade():
    op.execute("DROP FUNCTION IF EXISTS get_hostel_occupancy_and_revenue(INT) CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS get_top_performing_hostels() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS get_dashboard_and_activities() CASCADE;")
    op.execute("DROP FUNCTION IF EXISTS upsert_hostel() CASCADE;")
    op.execute("DROP TABLE IF EXISTS activities CASCADE;")
    op.execute("DROP TABLE IF EXISTS occupancies CASCADE;")
    op.execute("DROP TABLE IF EXISTS revenues CASCADE;")
    op.execute("DROP TABLE IF EXISTS admins CASCADE;")
    op.execute("DROP TABLE IF EXISTS hostels CASCADE;")
    op.execute("DROP TABLE IF EXISTS locations CASCADE;")

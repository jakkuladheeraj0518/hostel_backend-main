"""
Script to create all missing dashboard functions in the database
"""
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from sqlalchemy import text

def create_functions():
    # Create get_dashboard_and_activities function
    with open('fix_dashboard_function.sql', 'r') as f:
        sql = f.read()
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("✓ Function get_dashboard_and_activities created successfully!")
    
    # The get_top_performing_hostels was already fixed
    print("✓ Function get_top_performing_hostels already fixed!")
    
    # Create upsert_hostel function if needed
    upsert_sql = """
    DROP FUNCTION IF EXISTS upsert_hostel CASCADE;
    
    CREATE FUNCTION upsert_hostel(
        p_id INT,
        p_hostel_name TEXT,
        p_description TEXT,
        p_full_address TEXT,
        p_hostel_type TEXT,
        p_contact_email TEXT,
        p_contact_phone TEXT,
        p_amenities TEXT,
        p_rules TEXT,
        p_check_in TIME,
        p_check_out TIME,
        p_total_beds INT,
        p_current_occupancy INT,
        p_monthly_revenue NUMERIC,
        p_visibility TEXT DEFAULT 'public',
        p_is_featured BOOLEAN DEFAULT FALSE,
        p_location_id INT DEFAULT NULL
    )
    RETURNS TABLE (
        id INT, hostel_name TEXT, description TEXT, full_address TEXT, hostel_type TEXT,
        contact_email TEXT, contact_phone TEXT, amenities TEXT, rules TEXT,
        check_in TIME, check_out TIME, total_beds INT, current_occupancy INT,
        monthly_revenue NUMERIC, visibility TEXT, is_featured BOOLEAN,
        created_at TIMESTAMP, location_id INT
    )
    LANGUAGE plpgsql AS $$
    BEGIN
        IF p_id IS NOT NULL AND EXISTS (SELECT 1 FROM hostels WHERE hostels.id = p_id) THEN
            UPDATE hostels SET
                hostel_name = p_hostel_name, description = p_description,
                full_address = p_full_address, hostel_type = p_hostel_type,
                contact_email = p_contact_email, contact_phone = p_contact_phone,
                amenities = p_amenities, rules = p_rules, check_in = p_check_in,
                check_out = p_check_out, total_beds = p_total_beds,
                current_occupancy = p_current_occupancy, monthly_revenue = p_monthly_revenue,
                visibility = p_visibility, is_featured = p_is_featured, location_id = p_location_id
            WHERE hostels.id = p_id;
            RETURN QUERY SELECT * FROM hostels WHERE hostels.id = p_id;
        ELSE
            RETURN QUERY INSERT INTO hostels (
                hostel_name, description, full_address, hostel_type, contact_email,
                contact_phone, amenities, rules, check_in, check_out, total_beds,
                current_occupancy, monthly_revenue, visibility, is_featured, location_id
            ) VALUES (
                p_hostel_name, p_description, p_full_address, p_hostel_type,
                p_contact_email, p_contact_phone, p_amenities, p_rules, p_check_in,
                p_check_out, p_total_beds, p_current_occupancy, p_monthly_revenue,
                p_visibility, p_is_featured, p_location_id
            ) RETURNING *;
        END IF;
    END;
    $$;
    """
    
    with engine.connect() as conn:
        conn.execute(text(upsert_sql))
        conn.commit()
    
    print("✓ Function upsert_hostel created successfully!")
    
    # Create get_hostel_occupancy_and_revenue function
    occupancy_revenue_sql = """
    DROP FUNCTION IF EXISTS get_hostel_occupancy_and_revenue(INT) CASCADE;
    
    CREATE FUNCTION get_hostel_occupancy_and_revenue(p_hostel_id INT)
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
    """
    
    with engine.connect() as conn:
        conn.execute(text(occupancy_revenue_sql))
        conn.commit()
    
    print("✓ Function get_hostel_occupancy_and_revenue created successfully!")
    print("\n✅ All dashboard functions created successfully!")

if __name__ == "__main__":
    create_functions()

"""
Script to add unique constraint to admin_hostel_assignments table
"""
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from sqlalchemy import text

def add_unique_constraint():
    sql = """
    DO $$
    BEGIN
        -- Check if constraint doesn't exist before adding
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint 
            WHERE conname = 'uq_admin_hostel_assignment'
        ) THEN
            ALTER TABLE admin_hostel_assignments 
            ADD CONSTRAINT uq_admin_hostel_assignment 
            UNIQUE (admin_id, hostel_id);
        END IF;
    END $$;
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("✓ Unique constraint uq_admin_hostel_assignment added successfully!")

if __name__ == "__main__":
    add_unique_constraint()

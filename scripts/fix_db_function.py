"""
Script to fix the get_top_performing_hostels function in the database
"""
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from sqlalchemy import text

def fix_function():
    with open('fix_function.sql', 'r') as f:
        sql = f.read()
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("✓ Function get_top_performing_hostels updated successfully!")

if __name__ == "__main__":
    fix_function()

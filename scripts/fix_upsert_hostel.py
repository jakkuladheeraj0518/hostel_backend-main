import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.database import engine
from sqlalchemy import text

def fix_function():
    with open('fix_upsert_hostel.sql', 'r') as f:
        sql = f.read()
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("✓ upsert_hostel function updated successfully!")

if __name__ == "__main__":
    fix_function()

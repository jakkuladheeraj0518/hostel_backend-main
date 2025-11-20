"""
Run this script to apply `fix_upsert_hostel.sql` to the database using
the project's SQLAlchemy engine.

Usage (from project root):
    venv\Scripts\activate
    python scripts\install_upsert_hostel.py

This reads `fix_upsert_hostel.sql` and executes it inside a transaction.
"""

import sys
from pathlib import Path
from sqlalchemy import text

# Ensure project root is on sys.path so `import app` works when running
# the script directly (sys.path[0] is the script's directory by default).
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    # Import engine from the app
    from app.core.database import engine
except Exception as e:
    print("Failed to import app.core.database.engine:", e)
    print("Hint: run this from the project root or set PYTHONPATH=.")
    sys.exit(1)

sql_file = Path(__file__).resolve().parents[1] / 'fix_upsert_hostel.sql'
if not sql_file.exists():
    print(f"SQL file not found: {sql_file}")
    sys.exit(1)

sql = sql_file.read_text()

try:
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("Applied fix_upsert_hostel.sql successfully.")
except Exception as e:
    print("Failed to apply SQL:", e)
    sys.exit(1)

"""
Create all database tables directly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import Base, engine
from app.models.user import User
from app.models.hostel import Hostel
from app.models.admin_hostel_mapping import AdminHostelMapping
from app.models.session_context import SessionContext
from app.models.permission import Permission, RolePermission
from app.models.audit_log import AuditLog
from app.models.refresh_token import RefreshToken


def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully!")
        print("\nCreated tables:")
        for table in Base.metadata.tables:
            print(f"  - {table}")
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise


if __name__ == "__main__":
    create_tables()


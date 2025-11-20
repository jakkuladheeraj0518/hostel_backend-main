"""
Initialize default roles (SuperAdmin, Admin, etc.)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.core.roles import Role
from app.models.user import User
from sqlalchemy.orm import Session


def init_roles():
    """Initialize default roles in database"""
    db = SessionLocal()
    try:
        # Roles are stored as strings in the User model
        # This script can be used to verify roles exist
        print("Roles initialized:")
        for role in Role:
            print(f"  - {role.value}")
        print("\nRoles are managed via the Role enum in app.core.roles")
    finally:
        db.close()


if __name__ == "__main__":
    init_roles()


"""
Reset Database Script
Drops all tables and recreates them from scratch
"""
from app.core.database import engine, Base, drop_tables, create_tables

def reset_database():
    """Drop and recreate all database tables"""
    print("=" * 60)
    print("RESETTING DATABASE")
    print("=" * 60)
    
    # Import all models to register them with Base
    print("\nImporting models...")
    from app.models import (
        User, Hostel, Room, Bed, Student, Admin, Supervisor,
        LeaveApplication, Payment, Complaint, Notice, Booking,
        Review, Referral, Attendance, MessMenu, Maintenance, Visitor
    )
    
    # Drop all tables
    print("\nDropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("[OK] All tables dropped")
    except Exception as e:
        print(f"[WARNING] Error dropping tables: {e}")
    
    # Recreate all tables
    print("\nCreating all tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] All tables created successfully")
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("DATABASE RESET COMPLETE")
    print("=" * 60)
    print("\nYou can now run: python seed.py")
    return True


if __name__ == "__main__":
    reset_database()

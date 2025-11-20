"""
Automatically create a Super Admin user.

When you run:
    python scripts/create_super_admin.py

It will automatically create ONE superadmin with fixed details
if not already present in the database.
"""

from app.core.database import SessionLocal
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegister
from app.schemas.user import UserCreate
from app.core.roles import Role
from app.models.hostel import Hostel


def main():
    # Fixed Super Admin details (You can change these)
    SUPERADMIN_EMAIL = "superadmin@gmail.com"
    SUPERADMIN_USERNAME = "superadmin"
    SUPERADMIN_PASSWORD = "Admin@123"
    SUPERADMIN_FULL_NAME = "Default Super Admin"
    SUPERADMIN_PHONE = "8885277722"

    print("🔍 Checking if Super Admin already exists...")

    db = SessionLocal()
    try:
        svc = AuthService(db)

        # Check if user exists by email
        existing = svc.user_repo.get_by_email(SUPERADMIN_EMAIL)

        if existing:
            # Ensure role is SuperAdmin
            changed = False
            if existing.role != Role.SUPERADMIN.value:
                existing.role = Role.SUPERADMIN.value
                changed = True
            if not existing.is_active:
                existing.is_active = True
                changed = True
            if not existing.is_email_verified:
                existing.is_email_verified = True
                changed = True
            if changed:
                db.commit()
                print(f"✅ Existing user upgraded to SUPERADMIN: {existing.email}")
            else:
                print(f"ℹ️ Super Admin already exists: {existing.email}")
            return

        # Create a new superadmin if not found
        print("⚙️ Creating new Super Admin user...")

        # Ensure there is at least one Hostel record: some DB schemas require `hostel_id` NOT NULL
        hostel = db.query(Hostel).first()
        if not hostel:
            print("🏠 No hostel found. Creating default hostel...")
            # `hostel_name` is required by the Hostels table (not-null). Provide it here.
            hostel = Hostel(hostel_name="Default Hostel", name="Default Hostel", address="Auto-created by create_super_admin")
            db.add(hostel)
            try:
                db.commit()
                db.refresh(hostel)
                print(f"🏠 Created hostel id={hostel.id}")
            except Exception:
                db.rollback()
                raise

        # Build a UserCreate with hostel_id to satisfy NOT NULL constraints
        user_create = UserCreate(
            email=SUPERADMIN_EMAIL,
            phone_number=SUPERADMIN_PHONE,
            username=SUPERADMIN_USERNAME,
            password=SUPERADMIN_PASSWORD,
            full_name=SUPERADMIN_FULL_NAME,
            role=Role.SUPERADMIN.value,
        
        )

        # Create user directly via repository to ensure hostel_id is applied
        created = svc.user_repo.create(user_create)

        # Mark as active & verified
        created.is_active = True
        created.is_email_verified = True
        created.is_phone_verified = True
        created.role = Role.SUPERADMIN.value

        db.commit()

        print(f"✅ Super Admin Created Successfully")
        print(f"📧 Email: {SUPERADMIN_EMAIL}")
        print(f"👤 Username: {SUPERADMIN_USERNAME}")
        print(f"🔐 Password: {SUPERADMIN_PASSWORD}")

    finally:
        db.close()


if __name__ == "__main__":
    main()

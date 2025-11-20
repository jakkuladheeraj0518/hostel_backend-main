from app.core.database import SessionLocal
from app.models.payment_models import Customer
from app.models.hostel import Hostel
from app.models.admin import Admin, AdminHostelAssignment, PermissionLevel
from sqlalchemy.exc import IntegrityError

def seed_test_data():
    db = SessionLocal()
    try:
        existing_customer = db.query(Customer).filter_by(email="testuser@example.com").first()
        existing_hostel = db.query(Hostel).filter_by(hostel_name="Blue Horizon Hostel").first()

        if not existing_customer:
            customer = Customer(
                name="Test User",
                email="testuser@example.com",
                phone="9876543210"
            )
            db.add(customer)
        else:
            customer = existing_customer

        if not existing_hostel:
            hostel = Hostel(
                hostel_name="Blue Horizon Hostel",
                full_address="Main Street, City Center",
                capacity=150
            )
            db.add(hostel)
        else:
            hostel = existing_hostel

        db.commit()
        db.refresh(customer)
        db.refresh(hostel)

        print(f"✅ Customer ID: {customer.id}")
        print(f"✅ Hostel ID: {hostel.id}")

    except IntegrityError as e:
        db.rollback()
        print(f"❌ Integrity error: {e.orig}")
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_test_data()

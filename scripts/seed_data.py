"""
Seed initial data for Hostels, Rooms, Users, Bookings, Waitlist.
Run with:
  python scripts/seed_data.py
or:
  python -m scripts.seed_data
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, Base, engine
from app.models.hostel import Hostel
from app.models.rooms import Room, RoomType
from app.models.booking import Booking, BookingStatus
from app.models.waitlist import Waitlist
from app.models.user import User
from app.core.security import get_password_hash


# ---------------------------------------------------------
# HOSTELS
# ---------------------------------------------------------
def seed_hostels(db: Session):
    hostels = [
        Hostel(
            hostel_name="Sunrise Boys Hostel",
            name="Sunrise Boys Hostel",
            full_address="Near Metro Station, Hyderabad",
            city="Hyderabad",
            pincode="500072",
            description="Fully furnished rooms with 24/7 security",
            gender_type="Boys",
            amenities="Wifi,Laundry,Mess,Parking",
        ),
        Hostel(
            hostel_name="Elite Girls Residency",
            name="Elite Girls Residency",
            full_address="Kukatpally, Hyderabad",
            city="Hyderabad",
            pincode="500085",
            description="Safe and comfortable living for girls",
            gender_type="Girls",
            amenities="Wifi,Gym,Security,Mess",
        ),
    ]

    db.add_all(hostels)
    db.commit()
    for h in hostels:
        db.refresh(h)
    return hostels


# ---------------------------------------------------------
# ROOMS
# ---------------------------------------------------------
def seed_rooms(db: Session, hostels):
    rooms = [
        # Hostel 1
        Room(
            hostel_id=hostels[0].id,
            room_number="101",
            room_type=RoomType.SINGLE,
            monthly_price=8000,
            price=8000,
            room_capacity=1,
            total_beds=1,
            available_beds=1,
            availability=1,
            amenities="Wifi,AC",
        ),
        Room(
            hostel_id=hostels[0].id,
            room_number="102",
            room_type=RoomType.DOUBLE,
            monthly_price=6000,
            price=6000,
            room_capacity=2,
            total_beds=2,
            available_beds=2,
            availability=2,
            amenities="Wifi",
        ),
        Room(
            hostel_id=hostels[0].id,
            room_number="103",
            room_type=RoomType.TRIPLE,
            monthly_price=5000,
            price=5000,
            room_capacity=3,
            total_beds=3,
            available_beds=3,
            availability=3,
            amenities="Wifi,Fan",
        ),
        # Hostel 2
        Room(
            hostel_id=hostels[1].id,
            room_number="201",
            room_type=RoomType.SINGLE,
            monthly_price=7500,
            price=7500,
            room_capacity=1,
            total_beds=1,
            available_beds=1,
            availability=1,
            amenities="Wifi,AC",
        ),
        Room(
            hostel_id=hostels[1].id,
            room_number="202",
            room_type=RoomType.DOUBLE,
            monthly_price=5500,
            price=5500,
            room_capacity=2,
            total_beds=2,
            available_beds=2,
            availability=2,
            amenities="Wifi",
        ),
    ]

    db.add_all(rooms)
    db.commit()
    for r in rooms:
        db.refresh(r)
    return rooms


# ---------------------------------------------------------
# USERS
# ---------------------------------------------------------
def seed_users(db: Session):
    users = [
        User(
            name="Alice Tester",
            full_name="Alice Tester",
            email="alice@example.com",
            phone_number="911234567890",
            country_code="+91",
            username="alice",
            hashed_password=get_password_hash("test123"),
            role="visitor",
            is_active=True,
            is_email_verified=True,
            is_phone_verified=True,
        ),
        User(
            name="Bob Visitor",
            full_name="Bob Visitor",
            email="bob@example.com",
            phone_number="911098765432",
            country_code="+91",
            username="bob",
            hashed_password=get_password_hash("test123"),
            role="visitor",
            is_active=True,
            is_email_verified=True,
            is_phone_verified=True,
        ),
    ]

    db.add_all(users)
    db.commit()
    for u in users:
        db.refresh(u)
    return users


# ---------------------------------------------------------
# BOOKINGS
# ---------------------------------------------------------
def seed_bookings(db: Session, rooms, users):
    bookings = [
        Booking(
            visitor_id=users[0].id,
            hostel_id=rooms[0].hostel_id,
            room_id=rooms[0].id,
            check_in=datetime.utcnow() + timedelta(days=2),
            check_out=datetime.utcnow() + timedelta(days=30),
            amount_paid=2000,
            status=BookingStatus.confirmed.value,  # string column
        ),
        Booking(
            visitor_id=users[1].id,
            hostel_id=rooms[1].hostel_id,
            room_id=rooms[1].id,
            check_in=datetime.utcnow() + timedelta(days=5),
            check_out=datetime.utcnow() + timedelta(days=25),
            amount_paid=3000,
            status=BookingStatus.pending.value,
        ),
    ]

    db.add_all(bookings)
    db.commit()
    for b in bookings:
        db.refresh(b)
    return bookings


# ---------------------------------------------------------
# WAITLIST
# ---------------------------------------------------------
def seed_waitlist(db: Session, hostels):
    waitlist_entries = [
        Waitlist(
            hostel_id=hostels[0].id,
            room_type="single",
            visitor_id=999,
            priority=1,
        ),
        Waitlist(
            hostel_id=hostels[1].id,
            room_type="double",
            visitor_id=1000,
            priority=2,
        ),
    ]

    db.add_all(waitlist_entries)
    db.commit()
    return waitlist_entries


# ---------------------------------------------------------
# MAIN SEED RUNNER
# ---------------------------------------------------------
def run_seeder():
    print("🚀 Seeding Database...")

    # Ensure mappings are loaded
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    hostels = seed_hostels(db)
    print("✔ Hostels created")

    rooms = seed_rooms(db, hostels)
    print("✔ Rooms created")

    users = seed_users(db)
    print("✔ Users created")

    seed_bookings(db, rooms, users)
    print("✔ Bookings created")

    seed_waitlist(db, hostels)
    print("✔ Waitlist entries created")

    db.close()
    print("🎉 Seeding Completed Successfully!")


if __name__ == "__main__":
    run_seeder()
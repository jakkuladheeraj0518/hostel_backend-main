"""
Seed test data for Hostel Management System
Creates: Hostels, Rooms, Users (Visitors)
"""
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])

from app.core.database import SessionLocal, Base, engine
from app.models.hostel import Hostel, Location
from app.models.rooms import Room, RoomType
from app.models.user import User
from app.core.security import BcryptContext
from app.core.roles import Role


def seed_data():
    """Seed test data into the database"""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # ============================================
        # 1. CREATE LOCATIONS
        # ============================================
        print("🏙️  Creating locations...")
        
        bangalore = db.query(Location).filter(Location.city == "Bangalore").first()
        if not bangalore:
            bangalore = Location(city="Bangalore")
            db.add(bangalore)
            db.commit()
        
        delhi = db.query(Location).filter(Location.city == "Delhi").first()
        if not delhi:
            delhi = Location(city="Delhi")
            db.add(delhi)
            db.commit()
        
        print(f"✅ Locations created: Bangalore (ID: {bangalore.id}), Delhi (ID: {delhi.id})")
        
        # ============================================
        # 2. CREATE HOSTELS
        # ============================================
        print("\n🏨 Creating hostels...")
        
        # Hostel 1
        hostel1 = db.query(Hostel).filter(Hostel.hostel_name == "Budget Haven").first()
        if not hostel1:
            hostel1 = Hostel(
                hostel_name="Budget Haven",
                name="Budget Haven Bangalore",
                full_address="123 Brigade Road, Bangalore, Karnataka",
                address="123 Brigade Road",
                city="Bangalore",
                pincode="560001",
                description="Affordable and comfortable budget hostel",
                hostel_type="Budget",
                gender_type="Co-ed",
                amenities="WiFi, Kitchen, Laundry, Common Room",
                rules="No smoking, Quiet hours 10 PM - 8 AM",
                contact_email="budgethaven@hostel.com",
                contact_phone="+919876543210",
                check_in=datetime.strptime("14:00", "%H:%M").time(),
                check_out=datetime.strptime("11:00", "%H:%M").time()
            )
            db.add(hostel1)
            db.commit()
        
        # Hostel 2
        hostel2 = db.query(Hostel).filter(Hostel.hostel_name == "Premium Stay").first()
        if not hostel2:
            hostel2 = Hostel(
                hostel_name="Premium Stay",
                name="Premium Stay Delhi",
                full_address="456 Connaught Place, Delhi",
                address="456 Connaught Place",
                city="Delhi",
                pincode="110001",
                description="Premium hostel with luxury amenities",
                hostel_type="Premium",
                gender_type="Co-ed",
                amenities="WiFi, AC, Hot Water, Gym, Restaurant",
                rules="Check-in anytime, Checkout 12 PM",
                contact_email="premiumstay@hostel.com",
                contact_phone="+919876543211",
                check_in=datetime.strptime("12:00", "%H:%M").time(),
                check_out=datetime.strptime("12:00", "%H:%M").time()
            )
            db.add(hostel2)
            db.commit()
        
        print(f"✅ Hostels created: Budget Haven (ID: {hostel1.id}), Premium Stay (ID: {hostel2.id})")
        
        # ============================================
        # 3. CREATE ROOMS
        # ============================================
        print("\n🛏️  Creating rooms...")
        
        rooms_data = [
            # Budget Haven rooms
            {"hostel_id": hostel1.id, "room_number": "101", "room_type": RoomType.SINGLE, "room_capacity": 1, "monthly_price": 500},
            {"hostel_id": hostel1.id, "room_number": "102", "room_type": RoomType.DOUBLE, "room_capacity": 2, "monthly_price": 800},
            {"hostel_id": hostel1.id, "room_number": "103", "room_type": RoomType.DORM, "room_capacity": 6, "monthly_price": 300},
            {"hostel_id": hostel1.id, "room_number": "104", "room_type": RoomType.TRIPLE, "room_capacity": 3, "monthly_price": 600},
            
            # Premium Stay rooms
            {"hostel_id": hostel2.id, "room_number": "201", "room_type": RoomType.SINGLE, "room_capacity": 1, "monthly_price": 1200},
            {"hostel_id": hostel2.id, "room_number": "202", "room_type": RoomType.DOUBLE, "room_capacity": 2, "monthly_price": 1800},
            {"hostel_id": hostel2.id, "room_number": "203", "room_type": RoomType.SUITE, "room_capacity": 4, "monthly_price": 2500},
        ]
        
        created_rooms = []
        for room_data in rooms_data:
            existing_room = db.query(Room).filter(
                Room.hostel_id == room_data["hostel_id"],
                Room.room_number == room_data["room_number"]
            ).first()
            
            if not existing_room:
                room = Room(
                    hostel_id=room_data["hostel_id"],
                    room_number=room_data["room_number"],
                    room_type=room_data["room_type"],
                    room_capacity=room_data["room_capacity"],
                    total_beds=room_data["room_capacity"],
                    available_beds=room_data["room_capacity"],
                    monthly_price=room_data["monthly_price"]
                )
                db.add(room)
                db.flush()
                created_rooms.append(room)
        
        db.commit()
        print(f"✅ Created {len(created_rooms)} rooms")
        
        # ============================================
        # 4. CREATE TEST USERS (VISITORS)
        # ============================================
        print("\n👥 Creating test users (visitors)...")
        
        password_context = BcryptContext()
        
        users_data = [
            {
                "username": "visitor1",
                "email": "visitor1@example.com",
                "phone_number": "+919999999001",
                "full_name": "Visitor One",
                "password": "password123",
                "role": Role.VISITOR.value,
            },
            {
                "username": "visitor2",
                "email": "visitor2@example.com",
                "phone_number": "+919999999002",
                "full_name": "Visitor Two",
                "password": "password123",
                "role": Role.VISITOR.value,
            },
            {
                "username": "visitor3",
                "email": "visitor3@example.com",
                "phone_number": "+919999999003",
                "full_name": "Visitor Three",
                "password": "password123",
                "role": Role.VISITOR.value,
            },
        ]
        
        created_users = []
        for user_data in users_data:
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            
            if not existing_user:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    phone_number=user_data["phone_number"],
                    full_name=user_data["full_name"],
                    hashed_password=password_context.hash(user_data["password"]),
                    role=user_data["role"],
                    is_active=True,
                    is_email_verified=True,
                    is_phone_verified=True,
                )
                db.add(user)
                db.flush()
                created_users.append(user)
        
        db.commit()
        print(f"✅ Created {len(created_users)} test users")
        
        # ============================================
        # 5. PRINT SUMMARY
        # ============================================
        print("\n" + "="*60)
        print("📊 TEST DATA SUMMARY")
        print("="*60)
        
        total_hostels = db.query(Hostel).count()
        total_rooms = db.query(Room).count()
        total_users = db.query(User).filter(User.role == Role.VISITOR.value).count()
        
        print(f"✅ Total Hostels: {total_hostels}")
        print(f"✅ Total Rooms: {total_rooms}")
        print(f"✅ Total Visitor Users: {total_users}")
        
        print("\n📍 SAMPLE DATA FOR TESTING:")
        print("-" * 60)
        
        # Show sample hostels
        hostels = db.query(Hostel).limit(2).all()
        for h in hostels:
            print(f"\n🏨 Hostel: {h.hostel_name} (ID: {h.id})")
            rooms = db.query(Room).filter(Room.hostel_id == h.id).all()
            for r in rooms:
                print(f"   🛏️  Room {r.room_number}: {r.room_type.value} (ID: {r.id}, Capacity: {r.room_capacity}, Monthly Price: ${r.monthly_price})")
        
        # Show sample users
        users = db.query(User).filter(User.role == Role.VISITOR.value).limit(3).all()
        print("\n👥 Sample Users:")
        for u in users:
            print(f"   User: {u.username} (ID: {u.id}, Email: {u.email})")
        
        print("\n" + "="*60)
        print("✨ TEST DATA SEEDING COMPLETED!")
        print("="*60)
        print("\n💡 Example API Requests:")
        print("-" * 60)
        print("""
Create a Booking:
POST /visitor/bookings/
{
  "visitor_id": 1,
  "hostel_id": 1,
  "room_id": 1,
  "check_in": "2025-11-20T14:00:00Z",
  "check_out": "2025-11-23T11:00:00Z",
  "amount_paid": 1500
}

Get Hostel Calendar:
GET /admin/bookings/calendar?hostel_id=1

Get All Rooms in Hostel:
GET /hostels/1/rooms
        """)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

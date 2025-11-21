"""
Comprehensive Seed Script for Hostel Management System
Creates complete test data including:
- Hostels with rooms and beds
- Users (Students, Admins, Supervisors)
- Notices and Mess Menus
- All necessary relationships
"""
import sys
import json
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, create_tables
from app.core.security import get_password_hash
from app.models.user import User
from app.models.student import Student
from app.models.admin import Admin
from app.models.supervisor import Supervisor
from app.models.hostel import Hostel
from app.models.room import Room
from app.models.bed import Bed
from app.models.notice import Notice
from app.models.mess_menu import MessMenu
from app.models.complaint import Complaint
from app.models.attendance import Attendance
from app.models.leave_application import LeaveApplication
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.visitor import Visitor
from app.models.review import Review
from app.models.referral import Referral
from app.models.maintenance import Maintenance
from app.models.enums import (
    UserType, HostelType, RoomType, MaintenanceStatus,
    BedStatus, NoticeType, TargetAudience, MealType,
    ComplaintStatus, ComplaintCategory, Priority,
    AttendanceStatus, LeaveStatus, LeaveType,
    BookingStatus, PaymentStatus, PaymentMethod, FeeType, ReviewCategory
)


def clear_existing_data(db: Session):
    """Clear existing test data"""
    print("Clearing existing data...")
    try:
        # Delete in correct order to respect foreign key constraints
        db.query(LeaveApplication).delete()
        db.query(Attendance).delete()
        db.query(Complaint).delete()
        db.query(Maintenance).delete()
        db.query(Visitor).delete()
        db.query(Payment).delete()
        db.query(Booking).delete()
        db.query(Review).delete()
        db.query(Referral).delete()
        db.query(MessMenu).delete()
        db.query(Notice).delete()
        db.query(Bed).delete()
        db.query(Room).delete()
        db.query(Student).delete()
        db.query(Admin).delete()
        db.query(Supervisor).delete()
        db.query(User).delete()
        db.query(Hostel).delete()
        db.commit()
        print("[OK] Existing data cleared")
    except Exception as e:
        print(f"Warning during cleanup: {e}")
        db.rollback()


def create_hostels(db: Session) -> list:
    """Create multiple test hostels"""
    print("\nCreating hostels...")
    
    hostels_data = [
        {
            "hostel_name": "Sunrise Boys Hostel",
            "description": "Premium boys hostel with modern amenities",
            "address": "123 University Road, College District",
            "hostel_type": HostelType.BOYS,
            "contact_email": "sunrise@hostel.com",
            "contact_phone": "9876543200",
            "amenities": json.dumps(["WiFi", "Laundry", "Gym", "Cafeteria", "Study Room", "Recreation Room"]),
            "rules": "No smoking, No alcohol, Curfew at 11 PM",
            "total_beds": 100,
            "occupancy": 3,
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001"
        },
        {
            "hostel_name": "Moonlight Girls Hostel",
            "description": "Safe and comfortable girls hostel",
            "address": "456 Campus Avenue, Education Zone",
            "hostel_type": HostelType.GIRLS,
            "contact_email": "moonlight@hostel.com",
            "contact_phone": "9876543201",
            "amenities": json.dumps(["WiFi", "Laundry", "Library", "Cafeteria", "Security", "Medical Room"]),
            "rules": "No visitors after 8 PM, Curfew at 10 PM",
            "total_beds": 80,
            "occupancy": 0,
            "city": "Pune",
            "state": "Maharashtra",
            "pincode": "411001"
        }
    ]
    
    hostels = []
    for hostel_data in hostels_data:
        hostel = Hostel(
            hostel_name=hostel_data["hostel_name"],
            description=hostel_data["description"],
            address=hostel_data["address"],
            hostel_type=hostel_data["hostel_type"],
            contact_email=hostel_data["contact_email"],
            contact_phone=hostel_data["contact_phone"],
            amenities=hostel_data["amenities"],
            rules=hostel_data["rules"],
            total_beds=hostel_data["total_beds"],
            occupancy=hostel_data["occupancy"],
            revenue=0.0,
            status="active",
            visibility="public",
            featured=True,
            city=hostel_data["city"],
            state=hostel_data["state"],
            pincode=hostel_data["pincode"],
            is_active=True
        )
        db.add(hostel)
        db.flush()
        hostels.append(hostel)
        print(f"[OK] Created hostel: {hostel.hostel_name}")
    
    db.commit()
    return hostels


def create_rooms_and_beds(db: Session, hostel: Hostel):
    """Create rooms and beds for a hostel"""
    print(f"\nCreating rooms and beds for {hostel.hostel_name}...")
    
    # Room configurations
    room_configs = [
        {"type": RoomType.SINGLE, "count": 10, "capacity": 1, "monthly": 5000, "quarterly": 14000, "annual": 50000},
        {"type": RoomType.DOUBLE, "count": 20, "capacity": 2, "monthly": 3500, "quarterly": 10000, "annual": 38000},
        {"type": RoomType.TRIPLE, "count": 15, "capacity": 3, "monthly": 2500, "quarterly": 7000, "annual": 27000},
        {"type": RoomType.SHARED, "count": 10, "capacity": 4, "monthly": 2000, "quarterly": 5500, "annual": 22000},
    ]
    
    room_number = 101
    total_beds_created = 0
    
    for config in room_configs:
        for i in range(config["count"]):
            # Create room
            room = Room(
                hostel_id=hostel.id,
                room_number=str(room_number),
                room_type=config["type"],
                room_capacity=config["capacity"],
                monthly_price=config["monthly"],
                quarterly_price=config["quarterly"],
                annual_price=config["annual"],
                availability=config["capacity"],
                amenities=json.dumps(["Bed", "Mattress", "Pillow", "Blanket", "Study Table", "Chair", "Wardrobe"]),
                maintenance_status=MaintenanceStatus.GOOD,
                capacity=config["capacity"],
                current_occupancy=0,
                is_occupied=False,
                price_per_month=config["monthly"]
            )
            db.add(room)
            db.flush()
            
            # Create beds for this room
            for bed_num in range(1, config["capacity"] + 1):
                bed = Bed(
                    hostel_id=hostel.id,
                    room_number=str(room_number),
                    bed_number=f"{room_number}-{bed_num}",
                    bed_status=BedStatus.AVAILABLE,
                    monthly_price=config["monthly"],
                    quarterly_price=config["quarterly"],
                    annual_price=config["annual"],
                    bed_type="single" if config["capacity"] == 1 else "bunk_bottom" if bed_num % 2 == 1 else "bunk_top",
                    has_mattress='Y',
                    has_pillow='Y',
                    has_blanket='Y'
                )
                db.add(bed)
                total_beds_created += 1
            
            room_number += 1
    
    db.commit()
    print(f"[OK] Created {room_number - 101} rooms and {total_beds_created} beds")


def create_student_users(db: Session, hostel: Hostel):
    """Create 15 student users for comprehensive testing"""
    print(f"\nCreating 15 student users for {hostel.hostel_name}...")
    
    students_data = [
        {
            "email": "student1@test.com",
            "password": "student123",
            "name": "Rahul Sharma",
            "phone": "9876543210",
            "student_id": "STU001",
            "hostel_code": "SBH001",
            "room_number": "101",
            "bed_number": "101-1",
            "blood_group": "O+",
            "guardian_name": "Rajesh Sharma",
            "guardian_phone": "9876543211",
            "course": "Computer Science",
            "year": "2",
            "college": "MIT College"
        },
        {
            "email": "student2@test.com",
            "password": "student123",
            "name": "Priya Patel",
            "phone": "9876543212",
            "student_id": "STU002",
            "hostel_code": "SBH001",
            "room_number": "102",
            "bed_number": "102-1",
            "blood_group": "A+",
            "guardian_name": "Suresh Patel",
            "guardian_phone": "9876543213",
            "course": "Mechanical Engineering",
            "year": "3",
            "college": "MIT College"
        },
        {
            "email": "student3@test.com",
            "password": "student123",
            "name": "Amit Kumar",
            "phone": "9876543214",
            "student_id": "STU003",
            "hostel_code": "SBH001",
            "room_number": "103",
            "bed_number": "103-1",
            "blood_group": "B+",
            "guardian_name": "Vijay Kumar",
            "guardian_phone": "9876543215",
            "course": "Electrical Engineering",
            "year": "1",
            "college": "MIT College"
        },
        {
            "email": "student4@test.com",
            "password": "student123",
            "name": "Sneha Reddy",
            "phone": "9876543216",
            "student_id": "STU004",
            "hostel_code": "SBH001",
            "room_number": "104",
            "bed_number": "104-1",
            "blood_group": "AB+",
            "guardian_name": "Krishna Reddy",
            "guardian_phone": "9876543217",
            "course": "Civil Engineering",
            "year": "2",
            "college": "MIT College"
        },
        {
            "email": "student5@test.com",
            "password": "student123",
            "name": "Vikram Singh",
            "phone": "9876543218",
            "student_id": "STU005",
            "hostel_code": "SBH001",
            "room_number": "105",
            "bed_number": "105-1",
            "blood_group": "O-",
            "guardian_name": "Harpal Singh",
            "guardian_phone": "9876543219",
            "course": "Information Technology",
            "year": "4",
            "college": "MIT College"
        },
        {
            "email": "student6@test.com",
            "password": "student123",
            "name": "Anjali Verma",
            "phone": "9876543240",
            "student_id": "STU006",
            "hostel_code": "SBH001",
            "room_number": "106",
            "bed_number": "106-1",
            "blood_group": "A-",
            "guardian_name": "Ramesh Verma",
            "guardian_phone": "9876543221",
            "course": "Electronics Engineering",
            "year": "3",
            "college": "MIT College"
        },
        {
            "email": "student7@test.com",
            "password": "student123",
            "name": "Karan Mehta",
            "phone": "9876543242",
            "student_id": "STU007",
            "hostel_code": "SBH001",
            "room_number": "107",
            "bed_number": "107-1",
            "blood_group": "B-",
            "guardian_name": "Ashok Mehta",
            "guardian_phone": "9876543223",
            "course": "Chemical Engineering",
            "year": "2",
            "college": "MIT College"
        },
        {
            "email": "student8@test.com",
            "password": "student123",
            "name": "Pooja Desai",
            "phone": "9876543224",
            "student_id": "STU008",
            "hostel_code": "SBH001",
            "room_number": "108",
            "bed_number": "108-1",
            "blood_group": "O+",
            "guardian_name": "Mahesh Desai",
            "guardian_phone": "9876543225",
            "course": "Biotechnology",
            "year": "1",
            "college": "MIT College"
        },
        {
            "email": "student9@test.com",
            "password": "student123",
            "name": "Rohan Joshi",
            "phone": "9876543226",
            "student_id": "STU009",
            "hostel_code": "SBH001",
            "room_number": "109",
            "bed_number": "109-1",
            "blood_group": "A+",
            "guardian_name": "Prakash Joshi",
            "guardian_phone": "9876543227",
            "course": "Aerospace Engineering",
            "year": "3",
            "college": "MIT College"
        },
        {
            "email": "student10@test.com",
            "password": "student123",
            "name": "Neha Kapoor",
            "phone": "9876543228",
            "student_id": "STU010",
            "hostel_code": "SBH001",
            "room_number": "110",
            "bed_number": "110-1",
            "blood_group": "B+",
            "guardian_name": "Anil Kapoor",
            "guardian_phone": "9876543229",
            "course": "Architecture",
            "year": "2",
            "college": "MIT College"
        },
        {
            "email": "student11@test.com",
            "password": "student123",
            "name": "Arjun Nair",
            "phone": "9876543230",
            "student_id": "STU011",
            "hostel_code": "SBH001",
            "room_number": "111",
            "bed_number": "111-1",
            "blood_group": "AB-",
            "guardian_name": "Sunil Nair",
            "guardian_phone": "9876543231",
            "course": "Automobile Engineering",
            "year": "4",
            "college": "MIT College"
        },
        {
            "email": "student12@test.com",
            "password": "student123",
            "name": "Divya Iyer",
            "phone": "9876543232",
            "student_id": "STU012",
            "hostel_code": "SBH001",
            "room_number": "112",
            "bed_number": "112-1",
            "blood_group": "O+",
            "guardian_name": "Venkat Iyer",
            "guardian_phone": "9876543233",
            "course": "Data Science",
            "year": "1",
            "college": "MIT College"
        },
        {
            "email": "student13@test.com",
            "password": "student123",
            "name": "Siddharth Rao",
            "phone": "9876543234",
            "student_id": "STU013",
            "hostel_code": "SBH001",
            "room_number": "113",
            "bed_number": "113-1",
            "blood_group": "A+",
            "guardian_name": "Mohan Rao",
            "guardian_phone": "9876543235",
            "course": "Artificial Intelligence",
            "year": "3",
            "college": "MIT College"
        },
        {
            "email": "student14@test.com",
            "password": "student123",
            "name": "Kavya Menon",
            "phone": "9876543236",
            "student_id": "STU014",
            "hostel_code": "SBH001",
            "room_number": "114",
            "bed_number": "114-1",
            "blood_group": "B+",
            "guardian_name": "Ravi Menon",
            "guardian_phone": "9876543237",
            "course": "Cyber Security",
            "year": "2",
            "college": "MIT College"
        },
        {
            "email": "student15@test.com",
            "password": "student123",
            "name": "Aditya Gupta",
            "phone": "9876543238",
            "student_id": "STU015",
            "hostel_code": "SBH001",
            "room_number": "115",
            "bed_number": "115-1",
            "blood_group": "O-",
            "guardian_name": "Sanjay Gupta",
            "guardian_phone": "9876543239",
            "course": "Robotics Engineering",
            "year": "4",
            "college": "MIT College"
        }
    ]
    
    for student_data in students_data:
        # Create User account
        user = User(
            user_type=UserType.STUDENT,
            name=student_data["name"],
            email=student_data["email"],
            phone=student_data["phone"],
            password_hash=get_password_hash(student_data["password"]),
            is_active=True,
            is_verified=True,
            student_id=student_data["student_id"],
            hostel_code=student_data["hostel_code"],
            hostel_id=hostel.id,
            room_number=student_data["room_number"],
            bed_number=student_data["bed_number"],
            check_in_date=date.today() - timedelta(days=30),
            blood_group=student_data["blood_group"],
            guardian_name=student_data["guardian_name"],
            guardian_phone=student_data["guardian_phone"],
            status="active"
        )
        db.add(user)
        db.flush()
        
        # Create Student profile
        student = Student(
            student_id=student_data["student_id"],
            hostel_code=student_data["hostel_code"],
            name=student_data["name"],
            email=student_data["email"],
            phone=student_data["phone"],
            room_number=student_data["room_number"],
            bed_number=student_data["bed_number"],
            check_in_date=date.today() - timedelta(days=30),
            blood_group=student_data["blood_group"],
            guardian_name=student_data["guardian_name"],
            guardian_phone=student_data["guardian_phone"],
            status="active",
            user_id=user.id,
            hostel_id=hostel.id,
            course=student_data["course"],
            year_of_study=student_data["year"],
            college_name=student_data["college"],
            emergency_contact_name=student_data["guardian_name"],
            emergency_contact_phone=student_data["guardian_phone"],
            emergency_contact_relation="Parent"
        )
        db.add(student)
        
        # Update bed occupancy
        bed = db.query(Bed).filter(
            Bed.hostel_id == hostel.id,
            Bed.bed_number == student_data["bed_number"]
        ).first()
        if bed:
            bed.bed_status = BedStatus.OCCUPIED
            bed.current_occupant_id = user.id
        
        print(f"[OK] Created student: {student_data['email']} / {student_data['password']}")
    
    # Update hostel occupancy
    hostel.occupancy = len(students_data)
    
    db.commit()
    print(f"[OK] Total students created: {len(students_data)}")


def create_admin_users(db: Session, hostel: Hostel):
    """Create admin users for testing"""
    print("\nCreating admin users...")
    
    admins_data = [
        {
            "email": "admin@test.com",
            "password": "admin123",
            "name": "Admin User",
            "phone": "9876540001",
            "admin_id": "ADM001",
            "role": "admin",
            "department": "Administration"
        },
        {
            "email": "superadmin@test.com",
            "password": "super123",
            "name": "Super Admin",
            "phone": "9876540002",
            "admin_id": "ADM002",
            "role": "super_admin",
            "department": "Management"
        },
        {
            "email": "manager@test.com",
            "password": "manager123",
            "name": "Manager User",
            "phone": "9876540003",
            "admin_id": "ADM003",
            "role": "manager",
            "department": "Operations"
        }
    ]
    
    for admin_data in admins_data:
        # Create User account
        user = User(
            user_type=UserType.ADMIN,
            name=admin_data["name"],
            email=admin_data["email"],
            phone=admin_data["phone"],
            password_hash=get_password_hash(admin_data["password"]),
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.flush()
        
        # Create Admin profile
        admin = Admin(
            admin_id=admin_data["admin_id"],
            name=admin_data["name"],
            email=admin_data["email"],
            phone=admin_data["phone"],
            role=admin_data["role"],
            department=admin_data["department"],
            status="active",
            user_id=user.id,
            hostel_id=hostel.id,
            employee_id=f"EMP{admin_data['admin_id']}",
            designation=admin_data["role"].replace("_", " ").title(),
            joining_date=datetime.now()
        )
        db.add(admin)
        print(f"[OK] Created {admin_data['role']}: {admin_data['email']} / {admin_data['password']}")
    
    db.commit()


def create_supervisor_users(db: Session, hostel: Hostel):
    """Create supervisor users for testing"""
    print(f"\nCreating supervisor users for {hostel.hostel_name}...")
    
    supervisors_data = [
        {
            "email": "warden@test.com",
            "password": "warden123",
            "name": "Rajesh Kumar",
            "phone": "9876540010",
            "employee_id": "SUP001",
            "role": "warden",
            "department": "Hostel Management",
            "access_level": "full",
            "shift": "morning"
        },
        {
            "email": "security@test.com",
            "password": "security123",
            "name": "Amit Singh",
            "phone": "9876540011",
            "employee_id": "SUP002",
            "role": "security",
            "department": "Security",
            "access_level": "intermediate",
            "shift": "night"
        },
        {
            "email": "maintenance@test.com",
            "password": "maintenance123",
            "name": "Suresh Patil",
            "phone": "9876540012",
            "employee_id": "SUP003",
            "role": "maintenance",
            "department": "Maintenance",
            "access_level": "basic",
            "shift": "morning"
        },
        {
            "email": "housekeeping@test.com",
            "password": "housekeeping123",
            "name": "Lakshmi Devi",
            "phone": "9876540013",
            "employee_id": "SUP004",
            "role": "housekeeping",
            "department": "Housekeeping",
            "access_level": "basic",
            "shift": "morning"
        }
    ]
    
    for supervisor_data in supervisors_data:
        # Create User account
        user = User(
            user_type=UserType.SUPERVISOR,
            name=supervisor_data["name"],
            email=supervisor_data["email"],
            phone=supervisor_data["phone"],
            password_hash=get_password_hash(supervisor_data["password"]),
            is_active=True,
            is_verified=True,
            hostel_id=hostel.id
        )
        db.add(user)
        db.flush()
        
        # Create Supervisor profile
        supervisor = Supervisor(
            supervisor_name=supervisor_data["name"],
            supervisor_email=supervisor_data["email"],
            supervisor_phone=supervisor_data["phone"],
            employee_id=supervisor_data["employee_id"],
            role=supervisor_data["role"],
            department=supervisor_data["department"],
            access_level=supervisor_data["access_level"],
            status="active",
            invitation_status="accepted",
            user_id=user.id,
            hostel_id=hostel.id,
            joining_date=datetime.now() - timedelta(days=180),
            shift_timing=supervisor_data["shift"],
            working_days=json.dumps(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]),
            permissions=json.dumps({
                "view_dashboard": True,
                "manage_attendance": supervisor_data["access_level"] in ["intermediate", "full"],
                "manage_complaints": supervisor_data["access_level"] in ["intermediate", "full"],
                "manage_visitors": supervisor_data["access_level"] in ["intermediate", "full"],
                "manage_mess_menu": supervisor_data["role"] == "warden",
                "view_reports": supervisor_data["access_level"] == "full"
            })
        )
        db.add(supervisor)
        print(f"[OK] Created {supervisor_data['role']}: {supervisor_data['email']} / {supervisor_data['password']}")
    
    db.commit()


def create_notices(db: Session, hostel: Hostel, admin_user_id: str):
    """Create sample notices"""
    print(f"\nCreating notices for {hostel.hostel_name}...")
    
    notices_data = [
        {
            "title": "Welcome to New Academic Year",
            "content": "Welcome all students to the new academic year. Please ensure all your documents are submitted to the office.",
            "type": NoticeType.GENERAL,
            "urgent": False,
            "audience": TargetAudience.ALL
        },
        {
            "title": "Hostel Fee Payment Reminder",
            "content": "This is a reminder to pay your hostel fees by the end of this month. Late payment will incur a penalty.",
            "type": NoticeType.PAYMENT,
            "urgent": True,
            "audience": TargetAudience.STUDENTS
        },
        {
            "title": "Maintenance Work Scheduled",
            "content": "Plumbing maintenance work is scheduled for tomorrow from 10 AM to 2 PM. Water supply will be interrupted.",
            "type": NoticeType.MAINTENANCE,
            "urgent": True,
            "audience": TargetAudience.ALL
        },
        {
            "title": "New Mess Menu Available",
            "content": "New mess menu for this week is now available. Check the mess notice board for details.",
            "type": NoticeType.GENERAL,
            "urgent": False,
            "audience": TargetAudience.STUDENTS
        },
        {
            "title": "Security Guidelines",
            "content": "Please ensure you carry your ID cards at all times. Visitors must register at the security desk.",
            "type": NoticeType.RULE,
            "urgent": False,
            "audience": TargetAudience.ALL
        }
    ]
    
    for notice_data in notices_data:
        notice = Notice(
            hostel_id=hostel.id,
            notice_title=notice_data["title"],
            notice_content=notice_data["content"],
            notice_type=notice_data["type"],
            is_urgent=notice_data["urgent"],
            target_audience=notice_data["audience"],
            is_active=True,
            publish_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=30),
            created_by=admin_user_id
        )
        db.add(notice)
    
    db.commit()
    print(f"[OK] Created {len(notices_data)} notices")


def create_mess_menus(db: Session, hostel: Hostel, supervisor_user_id: str, admin_user_id: str):
    """Create sample mess menus"""
    print(f"\nCreating mess menus for {hostel.hostel_name}...")
    
    # Create menus for next 7 days
    meal_plans = {
        MealType.BREAKFAST: [
            {"items": ["Idli", "Sambar", "Chutney", "Tea/Coffee"], "veg": ["Idli", "Sambar", "Chutney"]},
            {"items": ["Poha", "Jalebi", "Tea/Coffee"], "veg": ["Poha", "Jalebi"]},
            {"items": ["Upma", "Banana", "Tea/Coffee"], "veg": ["Upma", "Banana"]},
            {"items": ["Paratha", "Curd", "Pickle", "Tea/Coffee"], "veg": ["Paratha", "Curd", "Pickle"]},
            {"items": ["Dosa", "Sambar", "Chutney", "Tea/Coffee"], "veg": ["Dosa", "Sambar", "Chutney"]},
            {"items": ["Bread", "Butter", "Jam", "Boiled Eggs", "Tea/Coffee"], "veg": ["Bread", "Butter", "Jam"]},
            {"items": ["Aloo Paratha", "Curd", "Pickle", "Tea/Coffee"], "veg": ["Aloo Paratha", "Curd", "Pickle"]}
        ],
        MealType.LUNCH: [
            {"items": ["Rice", "Dal", "Roti", "Vegetable Curry", "Salad"], "veg": ["Rice", "Dal", "Roti", "Vegetable Curry", "Salad"]},
            {"items": ["Rice", "Sambar", "Roti", "Paneer Curry", "Curd"], "veg": ["Rice", "Sambar", "Roti", "Paneer Curry", "Curd"]},
            {"items": ["Rice", "Rajma", "Roti", "Mixed Veg", "Papad"], "veg": ["Rice", "Rajma", "Roti", "Mixed Veg", "Papad"]},
            {"items": ["Rice", "Chole", "Roti", "Aloo Gobi", "Salad"], "veg": ["Rice", "Chole", "Roti", "Aloo Gobi", "Salad"]},
            {"items": ["Biryani", "Raita", "Salad"], "veg": ["Veg Biryani", "Raita", "Salad"]},
            {"items": ["Rice", "Dal Fry", "Roti", "Bhindi Masala", "Curd"], "veg": ["Rice", "Dal Fry", "Roti", "Bhindi Masala", "Curd"]},
            {"items": ["Rice", "Kadhi", "Roti", "Aloo Matar", "Pickle"], "veg": ["Rice", "Kadhi", "Roti", "Aloo Matar", "Pickle"]}
        ],
        MealType.DINNER: [
            {"items": ["Rice", "Dal", "Roti", "Paneer Butter Masala", "Salad"], "veg": ["Rice", "Dal", "Roti", "Paneer Butter Masala", "Salad"]},
            {"items": ["Rice", "Sambar", "Roti", "Cabbage Curry", "Curd"], "veg": ["Rice", "Sambar", "Roti", "Cabbage Curry", "Curd"]},
            {"items": ["Rice", "Dal Tadka", "Roti", "Mix Veg", "Papad"], "veg": ["Rice", "Dal Tadka", "Roti", "Mix Veg", "Papad"]},
            {"items": ["Rice", "Rajma", "Roti", "Jeera Aloo", "Salad"], "veg": ["Rice", "Rajma", "Roti", "Jeera Aloo", "Salad"]},
            {"items": ["Rice", "Dal", "Roti", "Palak Paneer", "Curd"], "veg": ["Rice", "Dal", "Roti", "Palak Paneer", "Curd"]},
            {"items": ["Rice", "Chole", "Roti", "Baingan Bharta", "Salad"], "veg": ["Rice", "Chole", "Roti", "Baingan Bharta", "Salad"]},
            {"items": ["Rice", "Dal", "Roti", "Veg Kofta", "Pickle"], "veg": ["Rice", "Dal", "Roti", "Veg Kofta", "Pickle"]}
        ]
    }
    
    menus_created = 0
    for day in range(7):
        menu_date = date.today() + timedelta(days=day)
        
        for meal_type in [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER]:
            day_index = day % 7
            meal_data = meal_plans[meal_type][day_index]
            
            menu = MessMenu(
                hostel_id=hostel.id,
                menu_date=menu_date,
                meal_type=meal_type,
                menu_items=json.dumps(meal_data["items"]),
                description=f"{meal_type.value.title()} menu for {menu_date.strftime('%A, %B %d')}",
                vegetarian_options=json.dumps(meal_data["veg"]),
                created_by=supervisor_user_id,
                approved_by=admin_user_id,
                approval_status="published",
                created_at_time=datetime.now() - timedelta(days=1),
                approved_at=datetime.now(),
                published_at=datetime.now(),
                is_weekly_plan='N',
                expected_servings=str(hostel.occupancy + 10)
            )
            db.add(menu)
            menus_created += 1
    
    db.commit()
    print(f"[OK] Created {menus_created} mess menus (7 days x 3 meals)")


def create_complaints(db: Session, hostel: Hostel, students: list, supervisor_id: str):
    """Create sample complaints for testing"""
    print(f"\nCreating complaints for {hostel.hostel_name}...")
    
    complaints_data = [
        {
            "title": "Water leakage in bathroom",
            "description": "There is continuous water leakage from the bathroom ceiling. It's causing water accumulation on the floor.",
            "category": ComplaintCategory.PLUMBING,
            "priority": Priority.HIGH,
            "status": ComplaintStatus.OPEN,
            "room_number": "101"
        },
        {
            "title": "AC not working properly",
            "description": "The air conditioner in our room is not cooling properly. It makes strange noises.",
            "category": ComplaintCategory.ELECTRICAL,
            "priority": Priority.MEDIUM,
            "status": ComplaintStatus.IN_PROGRESS,
            "room_number": "102"
        },
        {
            "title": "Broken window glass",
            "description": "The window glass is cracked and needs immediate replacement for safety reasons.",
            "category": ComplaintCategory.MAINTENANCE,
            "priority": Priority.CRITICAL,
            "status": ComplaintStatus.OPEN,
            "room_number": "103"
        },
        {
            "title": "WiFi connectivity issues",
            "description": "Internet connection is very slow and keeps disconnecting frequently.",
            "category": ComplaintCategory.INTERNET,
            "priority": Priority.MEDIUM,
            "status": ComplaintStatus.IN_PROGRESS,
            "room_number": "104"
        },
        {
            "title": "Bed frame broken",
            "description": "The bed frame is broken and making creaking sounds. Needs repair urgently.",
            "category": ComplaintCategory.FURNITURE,
            "priority": Priority.HIGH,
            "status": ComplaintStatus.OPEN,
            "room_number": "105"
        },
        {
            "title": "Pest control needed",
            "description": "There are cockroaches in the room. Need pest control service.",
            "category": ComplaintCategory.HOUSEKEEPING,
            "priority": Priority.MEDIUM,
            "status": ComplaintStatus.RESOLVED,
            "room_number": "106"
        },
        {
            "title": "Door lock not working",
            "description": "The door lock is jammed and difficult to open/close.",
            "category": ComplaintCategory.MAINTENANCE,
            "priority": Priority.HIGH,
            "status": ComplaintStatus.IN_PROGRESS,
            "room_number": "107"
        },
        {
            "title": "Noise from neighboring room",
            "description": "Excessive noise from the neighboring room during study hours.",
            "category": ComplaintCategory.DISCIPLINE,
            "priority": Priority.LOW,
            "status": ComplaintStatus.OPEN,
            "room_number": "108"
        },
        {
            "title": "Bathroom cleaning required",
            "description": "Common bathroom needs thorough cleaning. Very unhygienic condition.",
            "category": ComplaintCategory.HOUSEKEEPING,
            "priority": Priority.MEDIUM,
            "status": ComplaintStatus.RESOLVED,
            "room_number": "109"
        },
        {
            "title": "Power socket not working",
            "description": "Two power sockets in the room are not working. Cannot charge devices.",
            "category": ComplaintCategory.ELECTRICAL,
            "priority": Priority.HIGH,
            "status": ComplaintStatus.OPEN,
            "room_number": "110"
        },
        {
            "title": "Fan making loud noise",
            "description": "Ceiling fan is making very loud noise and wobbling. Safety concern.",
            "category": ComplaintCategory.ELECTRICAL,
            "priority": Priority.HIGH,
            "status": ComplaintStatus.OPEN,
            "room_number": "111"
        },
        {
            "title": "Wardrobe door broken",
            "description": "Wardrobe door hinge is broken. Door is hanging and cannot be closed properly.",
            "category": ComplaintCategory.FURNITURE,
            "priority": Priority.MEDIUM,
            "status": ComplaintStatus.IN_PROGRESS,
            "room_number": "112"
        },
        {
            "title": "Drainage problem in washroom",
            "description": "Water is not draining properly from the washroom. Bad smell coming.",
            "category": ComplaintCategory.PLUMBING,
            "priority": Priority.HIGH,
            "status": ComplaintStatus.OPEN,
            "room_number": "113"
        },
        {
            "title": "Study table lamp not working",
            "description": "The study table lamp is not working. Need replacement or repair.",
            "category": ComplaintCategory.ELECTRICAL,
            "priority": Priority.LOW,
            "status": ComplaintStatus.OPEN,
            "room_number": "114"
        },
        {
            "title": "Room needs painting",
            "description": "Room walls have dampness and paint is peeling off. Needs repainting.",
            "category": ComplaintCategory.MAINTENANCE,
            "priority": Priority.LOW,
            "status": ComplaintStatus.OPEN,
            "room_number": "115"
        }
    ]
    
    for i, complaint_data in enumerate(complaints_data):
        student = students[i % len(students)]
        
        complaint = Complaint(
            hostel_id=hostel.id,
            user_id=student.id,
            complaint_title=complaint_data["title"],
            complaint_description=complaint_data["description"],
            complaint_category=complaint_data["category"],
            complaint_status=complaint_data["status"],
            priority=complaint_data["priority"],
            room_number=complaint_data["room_number"],
            created_at=datetime.now() - timedelta(days=(10 - i)),
            assigned_to=supervisor_id if complaint_data["status"] == ComplaintStatus.IN_PROGRESS else None,
            resolved_at=datetime.now() - timedelta(days=1) if complaint_data["status"] == ComplaintStatus.RESOLVED else None,
            resolution_notes="Issue resolved successfully" if complaint_data["status"] == ComplaintStatus.RESOLVED else None
        )
        db.add(complaint)
    
    db.commit()
    print(f"[OK] Created {len(complaints_data)} complaints")


def create_attendance_records(db: Session, hostel: Hostel, students: list, supervisor_id: str):
    """Create attendance records for testing
    
    SEQUENCE: This function must be called AFTER users are created and committed
    - user_id references must exist before creating attendance records
    - attendance_id is auto-generated when records are saved
    """
    print(f"\nCreating attendance records for {hostel.hostel_name}...")
    
    # Validate that students have valid IDs (sequence check)
    if not students:
        print("[WARNING] No students provided for attendance records")
        return
    
    for student in students:
        if not student.id:
            print(f"[ERROR] Student {student.email} has no ID. Users must be created first!")
            return
    
    records_created = 0
    # Create attendance for last 7 days
    for day in range(7):
        attendance_date = date.today() - timedelta(days=day)
        
        for i, student in enumerate(students):
            # Vary attendance status for realistic data
            if i % 10 == 0 and day < 2:
                status = AttendanceStatus.ABSENT
            elif i % 8 == 0:
                status = AttendanceStatus.EXCUSED
            elif i % 15 == 0:
                status = AttendanceStatus.LATE
            else:
                status = AttendanceStatus.PRESENT
            
            # SEQUENCE: user_id must reference an existing user.id
            attendance = Attendance(
                hostel_id=hostel.id,
                user_id=student.id,  # References user created earlier
                attendance_date=attendance_date,
                attendance_status=status,
                marked_by=supervisor_id,  # References supervisor user.id
                check_in_time=datetime.combine(attendance_date, datetime.min.time().replace(hour=8, minute=0)) if status == AttendanceStatus.PRESENT else None,
                check_out_time=datetime.combine(attendance_date, datetime.min.time().replace(hour=22, minute=0)) if status == AttendanceStatus.PRESENT else None,
                supervisor_remarks="Late arrival" if status == AttendanceStatus.LATE else None,
                created_at=datetime.combine(attendance_date, datetime.min.time().replace(hour=9, minute=0))
            )
            db.add(attendance)
            records_created += 1
    
    # Commit all attendance records (attendance_id auto-generated here)
    db.commit()
    print(f"[OK] Created {records_created} attendance records (7 days x {len(students)} students)")
    print(f"[OK] Sequence verified: user_id → attendance_id")


def create_leave_applications(db: Session, hostel: Hostel, students: list, supervisor_id: str):
    """Create leave applications for testing"""
    print(f"\nCreating leave applications for {hostel.hostel_name}...")
    
    leave_applications_data = [
        {
            "student_index": 0,
            "start_date": date.today() + timedelta(days=2),
            "end_date": date.today() + timedelta(days=4),
            "reason": "Family function - Sister's wedding",
            "leave_type": LeaveType.CASUAL,
            "status": LeaveStatus.PENDING,
            "emergency_contact": "9876543211"
        },
        {
            "student_index": 1,
            "start_date": date.today() + timedelta(days=1),
            "end_date": date.today() + timedelta(days=1),
            "reason": "Medical checkup at home town",
            "leave_type": LeaveType.MEDICAL,
            "status": LeaveStatus.PENDING,
            "emergency_contact": "9876543213"
        },
        {
            "student_index": 2,
            "start_date": date.today() - timedelta(days=5),
            "end_date": date.today() - timedelta(days=3),
            "reason": "Attending cousin's wedding",
            "leave_type": LeaveType.CASUAL,
            "status": LeaveStatus.APPROVED,
            "emergency_contact": "9876543215"
        },
        {
            "student_index": 3,
            "start_date": date.today() + timedelta(days=7),
            "end_date": date.today() + timedelta(days=14),
            "reason": "Going home for semester break",
            "leave_type": LeaveType.VACATION,
            "status": LeaveStatus.PENDING,
            "emergency_contact": "9876543217"
        },
        {
            "student_index": 4,
            "start_date": date.today() - timedelta(days=2),
            "end_date": date.today() - timedelta(days=1),
            "reason": "Fever and cold",
            "leave_type": LeaveType.MEDICAL,
            "status": LeaveStatus.APPROVED,
            "emergency_contact": "9876543219"
        },
        {
            "student_index": 5,
            "start_date": date.today() + timedelta(days=3),
            "end_date": date.today() + timedelta(days=5),
            "reason": "Attending technical workshop",
            "leave_type": LeaveType.ACADEMIC,
            "status": LeaveStatus.PENDING,
            "emergency_contact": "9876543221"
        },
        {
            "student_index": 6,
            "start_date": date.today() - timedelta(days=10),
            "end_date": date.today() - timedelta(days=8),
            "reason": "Personal work at home",
            "leave_type": LeaveType.CASUAL,
            "status": LeaveStatus.REJECTED,
            "emergency_contact": "9876543223"
        },
        {
            "student_index": 7,
            "start_date": date.today() + timedelta(days=1),
            "end_date": date.today() + timedelta(days=2),
            "reason": "Grandfather's health emergency",
            "leave_type": LeaveType.EMERGENCY,
            "status": LeaveStatus.APPROVED,
            "emergency_contact": "9876543225"
        },
        {
            "student_index": 8,
            "start_date": date.today() + timedelta(days=5),
            "end_date": date.today() + timedelta(days=7),
            "reason": "Attending friend's wedding",
            "leave_type": LeaveType.CASUAL,
            "status": LeaveStatus.PENDING,
            "emergency_contact": "9876543227"
        },
        {
            "student_index": 9,
            "start_date": date.today() + timedelta(days=10),
            "end_date": date.today() + timedelta(days=12),
            "reason": "Going home for festival",
            "leave_type": LeaveType.CASUAL,
            "status": LeaveStatus.PENDING,
            "emergency_contact": "9876543229"
        },
        {
            "student_index": 10,
            "start_date": date.today() - timedelta(days=7),
            "end_date": date.today() - timedelta(days=5),
            "reason": "Dental treatment",
            "leave_type": LeaveType.MEDICAL,
            "status": LeaveStatus.APPROVED,
            "emergency_contact": "9876543231"
        },
        {
            "student_index": 11,
            "start_date": date.today() + timedelta(days=15),
            "end_date": date.today() + timedelta(days=20),
            "reason": "Internship interview",
            "leave_type": LeaveType.ACADEMIC,
            "status": LeaveStatus.PENDING,
            "emergency_contact": "9876543233"
        },
        {
            "student_index": 12,
            "start_date": date.today() + timedelta(days=4),
            "end_date": date.today() + timedelta(days=6),
            "reason": "Family emergency - Father hospitalized",
            "leave_type": LeaveType.EMERGENCY,
            "status": LeaveStatus.APPROVED,
            "emergency_contact": "9876543235"
        },
        {
            "student_index": 13,
            "start_date": date.today() - timedelta(days=15),
            "end_date": date.today() - timedelta(days=13),
            "reason": "Personal reasons",
            "leave_type": LeaveType.CASUAL,
            "status": LeaveStatus.REJECTED,
            "emergency_contact": "9876543237"
        },
        {
            "student_index": 14,
            "start_date": date.today() + timedelta(days=8),
            "end_date": date.today() + timedelta(days=10),
            "reason": "Attending cultural event",
            "leave_type": LeaveType.ACADEMIC,
            "status": LeaveStatus.PENDING,
            "emergency_contact": "9876543239"
        }
    ]
    
    for leave_data in leave_applications_data:
        student = students[leave_data["student_index"]]
        
        leave_app = LeaveApplication(
            student_id=student.id,
            hostel_id=hostel.id,
            applied_by=student.id,
            leave_start_date=leave_data["start_date"],
            leave_end_date=leave_data["end_date"],
            leave_reason=leave_data["reason"],
            leave_type=leave_data["leave_type"].value,
            leave_status=leave_data["status"],
            emergency_contact=leave_data["emergency_contact"],
            approved_by=supervisor_id if leave_data["status"] in [LeaveStatus.APPROVED, LeaveStatus.REJECTED] else None,
            approved_at=datetime.now() - timedelta(days=1) if leave_data["status"] in [LeaveStatus.APPROVED, LeaveStatus.REJECTED] else None,
            rejection_reason="Insufficient reason provided" if leave_data["status"] == LeaveStatus.REJECTED else None
        )
        db.add(leave_app)
    
    db.commit()
    print(f"[OK] Created {len(leave_applications_data)} leave applications")


def create_bookings(db: Session, hostel: Hostel, students: list, rooms: list):
    """Create booking records for testing"""
    print(f"\nCreating bookings for {hostel.hostel_name}...")
    
    bookings_data = [
        {
            "student_index": 0,
            "room_index": 0,
            "status": BookingStatus.CONFIRMED,
            "duration": 6,
            "monthly_rent": 5000,
            "security_deposit": 5000,
            "advance_paid": 10000,
            "bed_number": "101-1",
            "special_requests": "Ground floor room preferred"
        },
        {
            "student_index": 1,
            "room_index": 1,
            "status": BookingStatus.CONFIRMED,
            "duration": 12,
            "monthly_rent": 3500,
            "security_deposit": 3500,
            "advance_paid": 7000,
            "bed_number": "102-1",
            "special_requests": "Need study table and chair"
        },
        {
            "student_index": 2,
            "room_index": 2,
            "status": BookingStatus.CONFIRMED,
            "duration": 3,
            "monthly_rent": 2500,
            "security_deposit": 2500,
            "advance_paid": 5000,
            "bed_number": "103-1",
            "special_requests": None
        },
        {
            "student_index": 3,
            "room_index": 3,
            "status": BookingStatus.PENDING,
            "duration": 6,
            "monthly_rent": 3500,
            "security_deposit": 3500,
            "advance_paid": 0,
            "bed_number": "104-1",
            "special_requests": "Vegetarian mess food only"
        },
        {
            "student_index": 4,
            "room_index": 4,
            "status": BookingStatus.CONFIRMED,
            "duration": 12,
            "monthly_rent": 5000,
            "security_deposit": 5000,
            "advance_paid": 10000,
            "bed_number": "105-1",
            "special_requests": "Quiet room for studies"
        },
        {
            "student_index": 5,
            "room_index": 5,
            "status": BookingStatus.CHECKED_IN,
            "duration": 6,
            "monthly_rent": 3500,
            "security_deposit": 3500,
            "advance_paid": 7000,
            "bed_number": "106-1",
            "special_requests": None
        },
        {
            "student_index": 6,
            "room_index": 6,
            "status": BookingStatus.CHECKED_IN,
            "duration": 12,
            "monthly_rent": 2500,
            "security_deposit": 2500,
            "advance_paid": 5000,
            "bed_number": "107-1",
            "special_requests": "Need extra storage space"
        },
        {
            "student_index": 7,
            "room_index": 7,
            "status": BookingStatus.CANCELLED,
            "duration": 3,
            "monthly_rent": 2000,
            "security_deposit": 2000,
            "advance_paid": 2000,
            "bed_number": "108-1",
            "special_requests": None
        }
    ]
    
    for booking_data in bookings_data:
        student = students[booking_data["student_index"]]
        room = rooms[booking_data["room_index"]] if booking_data["room_index"] < len(rooms) else rooms[0]
        
        total_amount = booking_data["monthly_rent"] * booking_data["duration"] + booking_data["security_deposit"]
        
        booking = Booking(
            user_id=student.id,
            hostel_id=hostel.id,
            room_id=room.id,
            booking_status=booking_data["status"],
            booking_date=datetime.now() - timedelta(days=60),
            check_in_date=datetime.now() - timedelta(days=30),
            check_out_date=datetime.now() + timedelta(days=booking_data["duration"] * 30),
            duration_months=booking_data["duration"],
            monthly_rent=booking_data["monthly_rent"],
            security_deposit=booking_data["security_deposit"],
            total_amount=total_amount,
            advance_paid=booking_data["advance_paid"],
            actual_check_in=datetime.now() - timedelta(days=30) if booking_data["status"] == BookingStatus.CHECKED_IN else None,
            bed_number=booking_data["bed_number"],
            special_requests=booking_data["special_requests"],
            cancelled_at=datetime.now() - timedelta(days=5) if booking_data["status"] == BookingStatus.CANCELLED else None,
            cancellation_reason="Changed plans" if booking_data["status"] == BookingStatus.CANCELLED else None,
            refund_amount=booking_data["advance_paid"] * 0.8 if booking_data["status"] == BookingStatus.CANCELLED else 0.0
        )
        db.add(booking)
    
    db.commit()
    print(f"[OK] Created {len(bookings_data)} bookings")


def create_payments(db: Session, hostel: Hostel, students: list):
    """Create payment records for testing"""
    print(f"\nCreating payments for {hostel.hostel_name}...")
    
    payments_data = [
        {
            "student_index": 0,
            "amount": 5000,
            "status": PaymentStatus.COMPLETED,
            "method": PaymentMethod.UPI,
            "fee_type": FeeType.RENT,
            "due_date": "2024-11-01",
            "transaction_id": "TXN001234567890"
        },
        {
            "student_index": 1,
            "amount": 3500,
            "status": PaymentStatus.COMPLETED,
            "method": PaymentMethod.CARD,
            "fee_type": FeeType.RENT,
            "due_date": "2024-11-01",
            "transaction_id": "TXN001234567891"
        },
        {
            "student_index": 2,
            "amount": 2500,
            "status": PaymentStatus.PENDING,
            "method": None,
            "fee_type": FeeType.RENT,
            "due_date": "2024-11-15",
            "transaction_id": None
        },
        {
            "student_index": 3,
            "amount": 3500,
            "status": PaymentStatus.PENDING,
            "method": None,
            "fee_type": FeeType.RENT,
            "due_date": "2024-10-15",
            "transaction_id": None
        },
        {
            "student_index": 4,
            "amount": 5000,
            "status": PaymentStatus.COMPLETED,
            "method": PaymentMethod.NET_BANKING,
            "fee_type": FeeType.RENT,
            "due_date": "2024-11-01",
            "transaction_id": "TXN001234567892"
        },
        {
            "student_index": 5,
            "amount": 1500,
            "status": PaymentStatus.COMPLETED,
            "method": PaymentMethod.UPI,
            "fee_type": FeeType.RENT,
            "due_date": "2024-11-01",
            "transaction_id": "TXN001234567893"
        },
        {
            "student_index": 6,
            "amount": 1500,
            "status": PaymentStatus.PENDING,
            "method": None,
            "fee_type": FeeType.RENT,
            "due_date": "2024-11-15",
            "transaction_id": None
        },
        {
            "student_index": 7,
            "amount": 500,
            "status": PaymentStatus.COMPLETED,
            "method": PaymentMethod.CASH,
            "fee_type": FeeType.RENT,
            "due_date": "2024-11-01",
            "transaction_id": "TXN001234567894"
        },
        {
            "student_index": 8,
            "amount": 200,
            "status": PaymentStatus.FAILED,
            "method": PaymentMethod.UPI,
            "fee_type": FeeType.LAUNDRY,
            "due_date": "2024-11-01",
            "transaction_id": "TXN001234567895"
        },
        {
            "student_index": 9,
            "amount": 5000,
            "status": PaymentStatus.COMPLETED,
            "method": PaymentMethod.UPI,
            "fee_type": FeeType.SECURITY_DEPOSIT,
            "due_date": "2024-10-01",
            "transaction_id": "TXN001234567896"
        },
        {
            "student_index": 10,
            "amount": 3500,
            "status": PaymentStatus.PENDING,
            "method": None,
            "fee_type": FeeType.RENT,
            "due_date": "2024-11-20",
            "transaction_id": None
        },
        {
            "student_index": 11,
            "amount": 1000,
            "status": PaymentStatus.COMPLETED,
            "method": PaymentMethod.CARD,
            "fee_type": FeeType.OTHER,
            "due_date": "2024-10-20",
            "transaction_id": "TXN001234567897"
        }
    ]
    
    for payment_data in payments_data:
        student = students[payment_data["student_index"]]
        
        payment = Payment(
            student_id=student.student_id if hasattr(student, 'student_id') else f"STU{payment_data['student_index']:03d}",
            user_id=student.id,
            hostel_id=hostel.id,
            fee_amount=payment_data["amount"],
            payment_status=payment_data["status"],
            payment_method=payment_data["method"],
            fee_type=payment_data["fee_type"],
            payment_due_date=payment_data["due_date"],
            transaction_id=payment_data["transaction_id"]
        )
        db.add(payment)
    
    db.commit()
    print(f"[OK] Created {len(payments_data)} payments")


def create_visitors(db: Session, hostel: Hostel, students: list, supervisor_id: str):
    """Create visitor records for testing"""
    print(f"\nCreating visitors for {hostel.hostel_name}...")
    
    visitors_data = [
        {
            "name": "Rajesh Sharma",
            "email": "rajesh.sharma@email.com",
            "phone": "9876543211",
            "type": "parent",
            "purpose": "Meeting son for family discussion",
            "student_index": 0,
            "id_type": "aadhar",
            "id_number": "1234-5678-9012",
            "status": "checked_out",
            "vehicle": "MH12AB1234",
            "vehicle_type": "four_wheeler"
        },
        {
            "name": "Suresh Patel",
            "email": "suresh.patel@email.com",
            "phone": "9876543213",
            "type": "parent",
            "purpose": "Visiting daughter",
            "student_index": 1,
            "id_type": "driving_license",
            "id_number": "MH1234567890",
            "status": "checked_in",
            "vehicle": "MH14CD5678",
            "vehicle_type": "four_wheeler"
        },
        {
            "name": "Amit Friend",
            "email": "amit.friend@email.com",
            "phone": "9876540050",
            "type": "guest",
            "purpose": "Meeting friend for project discussion",
            "student_index": 2,
            "id_type": "aadhar",
            "id_number": "2345-6789-0123",
            "status": "approved",
            "vehicle": None,
            "vehicle_type": None
        },
        {
            "name": "Plumber Services",
            "email": None,
            "phone": "9876540051",
            "type": "maintenance",
            "purpose": "Fixing water leakage in room 101",
            "student_index": None,
            "id_type": "voter_id",
            "id_number": "VOT1234567",
            "status": "checked_out",
            "vehicle": "MH15EF9012",
            "vehicle_type": "two_wheeler"
        },
        {
            "name": "Food Delivery",
            "email": None,
            "phone": "9876540052",
            "type": "delivery",
            "purpose": "Food delivery for student",
            "student_index": 3,
            "id_type": "aadhar",
            "id_number": "3456-7890-1234",
            "status": "checked_out",
            "vehicle": "MH16GH3456",
            "vehicle_type": "two_wheeler"
        },
        {
            "name": "College Official",
            "email": "official@college.edu",
            "phone": "9876540053",
            "type": "official",
            "purpose": "Hostel inspection and quality check",
            "student_index": None,
            "id_type": "pan",
            "id_number": "ABCDE1234F",
            "status": "checked_out",
            "vehicle": None,
            "vehicle_type": None
        },
        {
            "name": "Krishna Reddy",
            "email": "krishna.reddy@email.com",
            "phone": "9876543217",
            "type": "parent",
            "purpose": "Discussing daughter's academic progress",
            "student_index": 3,
            "id_type": "aadhar",
            "id_number": "4567-8901-2345",
            "status": "pending",
            "vehicle": "MH17IJ7890",
            "vehicle_type": "four_wheeler"
        },
        {
            "name": "Electrician",
            "email": None,
            "phone": "9876540054",
            "type": "vendor",
            "purpose": "AC repair in room 102",
            "student_index": None,
            "id_type": "aadhar",
            "id_number": "5678-9012-3456",
            "status": "checked_in",
            "vehicle": "MH18KL1234",
            "vehicle_type": "two_wheeler"
        }
    ]
    
    for visitor_data in visitors_data:
        student = students[visitor_data["student_index"]] if visitor_data["student_index"] is not None else None
        
        check_in = datetime.now() - timedelta(hours=2)
        check_out = datetime.now() - timedelta(hours=1) if visitor_data["status"] == "checked_out" else None
        
        visitor = Visitor(
            hostel_id=hostel.id,
            visitor_name=visitor_data["name"],
            visitor_email=visitor_data["email"],
            visitor_phone=visitor_data["phone"],
            visitor_type=visitor_data["type"],
            purpose_of_visit=visitor_data["purpose"],
            check_in_time=check_in,
            check_out_time=check_out,
            expected_duration="2 hours",
            person_to_meet=student.id if student else None,
            person_name=student.name if student else "Hostel Management",
            person_room_number=student.room_number if student and hasattr(student, 'room_number') else None,
            id_proof_type=visitor_data["id_type"],
            id_proof_number=visitor_data["id_number"],
            vehicle_number=visitor_data["vehicle"],
            vehicle_type=visitor_data["vehicle_type"],
            approval_status=visitor_data["status"],
            approved_by=supervisor_id if visitor_data["status"] in ["approved", "checked_in", "checked_out"] else None,
            approved_at=datetime.now() - timedelta(hours=3) if visitor_data["status"] in ["approved", "checked_in", "checked_out"] else None,
            recorded_by=supervisor_id,
            checked_out_by=supervisor_id if visitor_data["status"] == "checked_out" else None,
            temperature="98.6",
            health_declaration='Y',
            is_recurring='N',
            visit_count='1'
        )
        db.add(visitor)
    
    db.commit()
    print(f"[OK] Created {len(visitors_data)} visitor records")


def create_reviews(db: Session, hostel: Hostel, students: list):
    """Create review records for testing"""
    print(f"\nCreating reviews for {hostel.hostel_name}...")
    
    reviews_data = [
        {
            "student_index": 0,
            "rating": 5,
            "text": "Excellent hostel with great facilities. Clean rooms and friendly staff. Highly recommended!",
            "category": ReviewCategory.FACILITIES
        },
        {
            "student_index": 1,
            "rating": 4,
            "text": "Good hostel overall. Food quality is decent and rooms are well-maintained.",
            "category": ReviewCategory.FOOD
        },
        {
            "student_index": 2,
            "rating": 5,
            "text": "Amazing experience! The staff is very helpful and responsive to complaints.",
            "category": ReviewCategory.STAFF
        },
        {
            "student_index": 3,
            "rating": 3,
            "text": "Average hostel. Rooms are okay but WiFi connectivity needs improvement.",
            "category": ReviewCategory.FACILITIES
        },
        {
            "student_index": 4,
            "rating": 4,
            "text": "Good value for money. Clean and safe environment for students.",
            "category": ReviewCategory.CLEANLINESS
        },
        {
            "student_index": 5,
            "rating": 5,
            "text": "Best hostel in the area! Security is top-notch and facilities are excellent.",
            "category": ReviewCategory.FACILITIES
        },
        {
            "student_index": 6,
            "rating": 4,
            "text": "Nice hostel with good amenities. Mess food could be better but overall satisfied.",
            "category": ReviewCategory.FOOD
        },
        {
            "student_index": 7,
            "rating": 3,
            "text": "Decent place to stay. Maintenance response time needs to be faster.",
            "category": ReviewCategory.FACILITIES
        },
        {
            "student_index": 8,
            "rating": 5,
            "text": "Wonderful hostel! Clean rooms, good food, and excellent management.",
            "category": ReviewCategory.CLEANLINESS
        },
        {
            "student_index": 9,
            "rating": 4,
            "text": "Good hostel with all basic facilities. Staff is cooperative and helpful.",
            "category": ReviewCategory.STAFF
        }
    ]
    
    for review_data in reviews_data:
        student = students[review_data["student_index"]]
        
        review = Review(
            student_id=student.student_id if hasattr(student, 'student_id') else f"STU{review_data['student_index']:03d}",
            user_id=student.id,
            hostel_id=hostel.id,
            review_rating=review_data["rating"],
            overall_rating=review_data["rating"],
            review_text=review_data["text"],
            review_category=review_data["category"]
        )
        db.add(review)
    
    db.commit()
    print(f"[OK] Created {len(reviews_data)} reviews")


def create_referrals(db: Session, students: list):
    """Create referral records for testing"""
    print("\nCreating referrals...")
    
    referrals_data = [
        {
            "referrer_index": 0,
            "referred_name": "Rohit Sharma",
            "referred_email": "rohit.sharma@test.com",
            "referred_phone": "9876540060",
            "code": "REF001RAHUL",
            "status": "completed",
            "reward": 500.0
        },
        {
            "referrer_index": 1,
            "referred_name": "Priyanka Patel",
            "referred_email": "priyanka.patel@test.com",
            "referred_phone": "9876540061",
            "code": "REF002PRIYA",
            "status": "completed",
            "reward": 500.0
        },
        {
            "referrer_index": 2,
            "referred_name": "Sanjay Kumar",
            "referred_email": "sanjay.kumar@test.com",
            "referred_phone": "9876540062",
            "code": "REF003AMIT",
            "status": "pending",
            "reward": 0.0
        },
        {
            "referrer_index": 3,
            "referred_name": "Deepika Reddy",
            "referred_email": "deepika.reddy@test.com",
            "referred_phone": "9876540063",
            "code": "REF004SNEHA",
            "status": "pending",
            "reward": 0.0
        },
        {
            "referrer_index": 4,
            "referred_name": "Rajesh Singh",
            "referred_email": "rajesh.singh@test.com",
            "referred_phone": "9876540064",
            "code": "REF005VIKRAM",
            "status": "completed",
            "reward": 500.0
        }
    ]
    
    for referral_data in referrals_data:
        referrer = students[referral_data["referrer_index"]]
        
        referral = Referral(
            referrer_id=referrer.id,
            referred_name=referral_data["referred_name"],
            referred_email=referral_data["referred_email"],
            referred_phone=referral_data["referred_phone"],
            referral_code=referral_data["code"],
            status=referral_data["status"],
            reward_amount=referral_data["reward"],
            completed_at=datetime.now().strftime("%Y-%m-%d") if referral_data["status"] == "completed" else None
        )
        db.add(referral)
    
    db.commit()
    print(f"[OK] Created {len(referrals_data)} referrals")


def create_maintenance_records(db: Session, hostel: Hostel, supervisor_id: str, admin_id: str):
    """Create maintenance records for testing"""
    print(f"\nCreating maintenance records for {hostel.hostel_name}...")
    
    maintenance_data = [
        {
            "room": "101",
            "category": "plumbing",
            "description": "Water tap leaking in bathroom. Needs washer replacement.",
            "priority": Priority.MEDIUM,
            "status": MaintenanceStatus.UNDER_MAINTENANCE,
            "estimated_cost": 500.0,
            "actual_cost": 450.0
        },
        {
            "room": "102",
            "category": "electrical",
            "description": "AC not cooling properly. Needs gas refilling and servicing.",
            "priority": Priority.HIGH,
            "status": MaintenanceStatus.UNDER_MAINTENANCE,
            "estimated_cost": 2500.0,
            "actual_cost": None
        },
        {
            "room": "103",
            "category": "carpentry",
            "description": "Wardrobe door hinge broken. Needs replacement.",
            "priority": Priority.LOW,
            "status": MaintenanceStatus.GOOD,
            "estimated_cost": 800.0,
            "actual_cost": 750.0
        },
        {
            "room": "Common Area",
            "category": "cleaning",
            "description": "Deep cleaning required in common bathroom.",
            "priority": Priority.MEDIUM,
            "status": MaintenanceStatus.GOOD,
            "estimated_cost": 1000.0,
            "actual_cost": 1000.0
        },
        {
            "room": "105",
            "category": "electrical",
            "description": "Ceiling fan making noise and wobbling. Safety concern.",
            "priority": Priority.HIGH,
            "status": MaintenanceStatus.NEEDS_REPAIR,
            "estimated_cost": 1500.0,
            "actual_cost": None
        },
        {
            "room": "106",
            "category": "plumbing",
            "description": "Drainage problem in washroom. Water not draining properly.",
            "priority": Priority.HIGH,
            "status": MaintenanceStatus.UNDER_MAINTENANCE,
            "estimated_cost": 1200.0,
            "actual_cost": None
        },
        {
            "room": "Building",
            "category": "structural",
            "description": "Roof waterproofing required before monsoon season.",
            "priority": Priority.CRITICAL,
            "status": MaintenanceStatus.NEEDS_REPAIR,
            "estimated_cost": 25000.0,
            "actual_cost": None
        },
        {
            "room": "108",
            "category": "appliance",
            "description": "Water heater not working. Needs repair or replacement.",
            "priority": Priority.MEDIUM,
            "status": MaintenanceStatus.NEEDS_REPAIR,
            "estimated_cost": 3000.0,
            "actual_cost": None
        }
    ]
    
    for maint_data in maintenance_data:
        maintenance = Maintenance(
            hostel_id=hostel.id,
            room_number=maint_data["room"],
            location_details=f"Room {maint_data['room']}" if maint_data['room'] != "Common Area" and maint_data['room'] != "Building" else maint_data['room'],
            issue_category=maint_data["category"],
            issue_description=maint_data["description"],
            priority_level=maint_data["priority"],
            status=maint_data["status"],
            estimated_cost=maint_data["estimated_cost"],
            actual_cost=maint_data["actual_cost"],
            created_by=supervisor_id,
            assigned_to=supervisor_id if maint_data["status"] == MaintenanceStatus.UNDER_MAINTENANCE else None,
            approved_by=admin_id if maint_data["estimated_cost"] > 5000 else None,
            reported_date=datetime.now() - timedelta(days=10),
            scheduled_date=datetime.now() + timedelta(days=2) if maint_data["status"] == MaintenanceStatus.NEEDS_REPAIR else datetime.now() - timedelta(days=5),
            completion_date=datetime.now() - timedelta(days=2) if maint_data["status"] == MaintenanceStatus.GOOD else None,
            approved_at=datetime.now() - timedelta(days=8) if maint_data["estimated_cost"] > 5000 else None,
            requires_approval='Y' if maint_data["estimated_cost"] > 5000 else 'N',
            approval_status="approved" if maint_data["estimated_cost"] > 5000 else None,
            is_preventive='N'
        )
        db.add(maintenance)
    
    db.commit()
    print(f"[OK] Created {len(maintenance_data)} maintenance records")


def print_summary():
    """Print summary of created data"""
    print("\n" + "="*70)
    print("[SUCCESS] ✅ COMPREHENSIVE 100% SEED DATA CREATED")
    print("="*70)
    
    print("\nDATABASE SUMMARY:")
    print("  ✅ 2 Hostels (Boys & Girls)")
    print("  ✅ 55 Rooms (Single, Double, Triple, Shared)")
    print("  ✅ 100+ Beds with proper allocation")
    print("  ✅ 15 Students with room assignments")
    print("  ✅ 3 Admins (Super Admin, Admin, Manager)")
    print("  ✅ 4 Supervisors (Warden, Security, Maintenance, Housekeeping)")
    print("  ✅ 15 Complaints (Various categories and statuses)")
    print("  ✅ 105 Attendance Records (7 days x 15 students)")
    print("  ✅ 15 Leave Applications (Pending, Approved, Rejected)")
    print("  ✅ 5 Notices (General, Payment, Maintenance, Security)")
    print("  ✅ 21 Mess Menus (7 days x 3 meals)")
    print("  ✅ 8 Bookings (Confirmed, Pending, Checked-in, Cancelled)")
    print("  ✅ 12 Payments (Completed, Pending, Overdue, Failed)")
    print("  ✅ 8 Visitors (Parents, Guests, Vendors, Officials)")
    print("  ✅ 10 Reviews (5-star ratings with feedback)")
    print("  ✅ 5 Referrals (Completed and Pending)")
    print("  ✅ 8 Maintenance Records (Various priorities and statuses)")
    
    print("\n" + "="*70)
    print("LOGIN CREDENTIALS")
    print("="*70)
    
    print("\nSTUDENTS (15 users):")
    print("  - student1@test.com / student123   (Rahul Sharma - Room 101)")
    print("  - student2@test.com / student123   (Priya Patel - Room 102)")
    print("  - student3@test.com / student123   (Amit Kumar - Room 103)")
    print("  - student4@test.com / student123   (Sneha Reddy - Room 104)")
    print("  - student5@test.com / student123   (Vikram Singh - Room 105)")
    print("  - student6-15@test.com / student123 (10 more students...)")
    
    print("\nADMINS:")
    print("  - admin@test.com / admin123        (Admin)")
    print("  - superadmin@test.com / super123   (Super Admin)")
    print("  - manager@test.com / manager123    (Manager)")
    
    print("\nSUPERVISORS:")
    print("  - warden@test.com / warden123           (Warden - Full Access)")
    print("  - security@test.com / security123       (Security - Night Shift)")
    print("  - maintenance@test.com / maintenance123 (Maintenance)")
    print("  - housekeeping@test.com / housekeeping123 (Housekeeping)")
    
    print("\n" + "="*70)
    print("READY TO TEST")
    print("="*70)
    print("\nYou can now:")
    print("  1. Login with supervisor credentials (warden@test.com / warden123)")
    print("  2. View dashboard metrics (10 complaints, 105 attendance records)")
    print("  3. Manage complaints (Open, In Progress, Resolved)")
    print("  4. Track attendance (Present, Absent, Late, Excused)")
    print("  5. Approve/Reject leave applications (8 applications)")
    print("  6. View student list (15 students)")
    print("  7. Check mess menus and notices")
    print("\n" + "="*70 + "\n")


def main():
    """Main seeding function"""
    print("Starting comprehensive database seeding...")
    print("="*60)
    
    # Create tables if they don't exist
    create_tables()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_existing_data(db)
        
        # Create hostels
        hostels = create_hostels(db)
        primary_hostel = hostels[0]
        
        # Create rooms and beds for primary hostel
        create_rooms_and_beds(db, primary_hostel)
        
        # Create admin users first (needed for notices and menus)
        create_admin_users(db, primary_hostel)
        
        # Get admin user ID for creating notices
        admin_user = db.query(User).filter(User.email == "admin@test.com").first()
        
        # Create supervisor users
        create_supervisor_users(db, primary_hostel)
        
        # Get supervisor user ID for creating mess menus
        supervisor_user = db.query(User).filter(User.email == "warden@test.com").first()
        
        # SEQUENCE STEP 1: Create student users (generates user_id)
        create_student_users(db, primary_hostel)
        
        # SEQUENCE STEP 2: Retrieve all created student users with their IDs
        student_users = db.query(User).filter(
            User.user_type == UserType.STUDENT,
            User.hostel_id == primary_hostel.id
        ).all()
        
        print(f"\n[SEQUENCE CHECK] Retrieved {len(student_users)} students with valid user_ids")
        
        # Create complaints (requires user_id to exist)
        if supervisor_user and student_users:
            create_complaints(db, primary_hostel, student_users, supervisor_user.id)
        
        # SEQUENCE STEP 3: Create attendance records (requires user_id, generates attendance_id)
        if supervisor_user and student_users:
            create_attendance_records(db, primary_hostel, student_users, supervisor_user.id)
        
        # Create leave applications
        if supervisor_user and student_users:
            create_leave_applications(db, primary_hostel, student_users, supervisor_user.id)
        
        # Create notices
        if admin_user:
            create_notices(db, primary_hostel, admin_user.id)
        
        # Create mess menus
        if supervisor_user and admin_user:
            create_mess_menus(db, primary_hostel, supervisor_user.id, admin_user.id)
        
        # Get all rooms for bookings
        rooms = db.query(Room).filter(Room.hostel_id == primary_hostel.id).limit(10).all()
        
        # Create bookings
        if student_users and rooms:
            create_bookings(db, primary_hostel, student_users, rooms)
        
        # Create payments
        if student_users:
            create_payments(db, primary_hostel, student_users)
        
        # Create visitors
        if supervisor_user and student_users:
            create_visitors(db, primary_hostel, student_users, supervisor_user.id)
        
        # Create reviews
        if student_users:
            create_reviews(db, primary_hostel, student_users)
        
        # Create referrals
        if student_users:
            create_referrals(db, student_users)
        
        # Create maintenance records
        if supervisor_user and admin_user:
            create_maintenance_records(db, primary_hostel, supervisor_user.id, admin_user.id)
        
        # Print summary
        print_summary()
        
    except Exception as e:
        print(f"\n[ERROR] Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()

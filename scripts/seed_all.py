"""
Seed core data into the hostelB database.

Run:
    python -m scripts.seed_all
"""

from datetime import datetime, timedelta, date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.core.security import get_password_hash
from app.core.roles import Role
from app.utils.util import get_or_create

# Core / locations / hostels / rooms / beds
from app.models.hostel import Hostel, Location
from app.models.rooms import Room, RoomType
from app.models.beds import Bed, BedStatus

# Users & sessions
from app.models.user import User
from app.models.session_context import SessionContext

# Admin & mappings
from app.models.admin import Admin, AdminHostelAssignment, PermissionLevel

# Students & related
from app.models.students import (
    Student,
    StudentPayment,
    Attendance as StudentAttendance,
    StudentDocument,
    PaymentType as StudentPaymentType,
    PaymentMethod as StudentPaymentMethod,
    AttendanceMode as StudentAttendanceMode,
)

# Supervisors
from app.models.supervisors import Supervisor, SupervisorRole, Department, AccessLevel, SupervisorHostel, SupervisorActivity, AdminOverride

# Fee structure
from app.models.fee_structure_models import FeePlan, SecurityDeposit, MessCharge, AdditionalService, FeeFrequency

# Subscription & payments (subscription-level)
from app.models.subscription import (
    SubscriptionPlan,
    Subscription,
    Payment as SubPayment,
    SubscriptionStatus,
    BillingCycle,
    PlanTier,
    PaymentStatus as SubPaymentStatus,
    PaymentType as SubPaymentType,
    SubscriptionChange,
    ChangeType,
)

# Payment & invoices (per-user)
from app.models.payment_models import (
    Invoice,
    Transaction,
    Receipt,
    RefundRequest,
    TransactionType,
    PaymentStatus,
    ReminderConfiguration,
    PaymentReminder,
    ReminderType,
    ReminderChannel,
    ReminderStatus,
    ReminderTemplate,
    Customer,
    PaymentWebhook,
    Refund,
)

# Waitlist / booking
from app.models.waitlist import Waitlist
from app.models.booking import Booking, BookingStatus

# Mess menu
from app.models.mess_menu import MessMenu, MenuType, MealType, MenuStatus, MenuFeedback, MealPreference, DietType

# Announcements
from app.models.announcement import Announcement, AnnouncementStatus, AnnouncementCategory

# Reports (operational/marketing)
from app.models.reports import (
    Attendance as ReportAttendance,
    FinancialTransaction,
    HostelBooking,
    HostelProfileView,
    SearchQuery,
)

# Report models (analytics)
from app.models.report_models import (
    BookingReport,
    Commission,
    SubscriptionRevenue,
    Report,
    FinancialSummary,
    BookingStatus as ReportBookingStatus,
    PaymentStatus as ReportPaymentStatus,
    CommissionStatus,
    ReportType,
    ExportFormat,
)

# Notifications
from app.models.notification import Notification, NotificationTemplate, DeviceToken, Channel


# ---------------------------------------------------------
# Seeding helpers
# ---------------------------------------------------------

def seed_locations(db: Session):
    hyd, _ = get_or_create(db, Location, id=1, defaults={"city": "Hyderabad"})
    blr, _ = get_or_create(db, Location, id=2, defaults={"city": "Bangalore"})
    return [hyd, blr]


def seed_hostels(db: Session, locations):
    hyd, blr = locations

    h1, _ = get_or_create(
        db,
        Hostel,
        hostel_name="Sunrise Boys Hostel",
        defaults={
            "name": "Sunrise Boys Hostel",
            "full_address": "Near Metro Station, Hyderabad",
            "city": hyd.city,
            "pincode": "500072",
            "description": "Fully furnished rooms with 24/7 security",
            "gender_type": "Boys",
            "amenities": "Wifi,Laundry,Mess,Parking",
            "location_id": hyd.id,
            "total_beds": 30,
            "current_occupancy": 0,
        },
    )

    h2, _ = get_or_create(
        db,
        Hostel,
        hostel_name="Elite Girls Residency",
        defaults={
            "name": "Elite Girls Residency",
            "full_address": "Kukatpally, Hyderabad",
            "city": hyd.city,
            "pincode": "500085",
            "description": "Safe and comfortable living for girls",
            "gender_type": "Girls",
            "amenities": "Wifi,Gym,Security,Mess",
            "location_id": hyd.id,
            "total_beds": 20,
            "current_occupancy": 0,
        },
    )

    h3, _ = get_or_create(
        db,
        Hostel,
        hostel_name="Tech Hub Hostel",
        defaults={
            "name": "Tech Hub Hostel",
            "full_address": "Outer Ring Road, Bangalore",
            "city": blr.city,
            "pincode": "560103",
            "description": "Co-ed hostel for tech professionals",
            "gender_type": "Co-ed",
            "amenities": "Wifi,Gym,Mess,Parking",
            "location_id": blr.id,
            "total_beds": 40,
            "current_occupancy": 0,
        },
    )

    return [h1, h2, h3]


def seed_rooms(db: Session, hostels):
    rooms = []
    for hostel in hostels:
        r1, _ = get_or_create(
            db,
            Room,
            hostel_id=hostel.id,
            room_number=f"{hostel.id}01",
            defaults={
                "room_type": RoomType.SINGLE,
                "monthly_price": 8000,
                "price": 8000,
                "room_capacity": 1,
                "total_beds": 1,
                "available_beds": 1,
                "availability": 1,
                "amenities": "Wifi,AC",
            },
        )
        r2, _ = get_or_create(
            db,
            Room,
            hostel_id=hostel.id,
            room_number=f"{hostel.id}02",
            defaults={
                "room_type": RoomType.DOUBLE,
                "monthly_price": 6000,
                "price": 6000,
                "room_capacity": 2,
                "total_beds": 2,
                "available_beds": 2,
                "availability": 2,
                "amenities": "Wifi",
            },
        )
        rooms.extend([r1, r2])
    return rooms


def seed_beds(db: Session, rooms):
    beds = []
    for room in rooms:
        for i in range(room.total_beds):
            bed, _ = get_or_create(
                db,
                Bed,
                room_number=room.room_number,
                bed_number=f"{room.room_number}-{i+1}",
                defaults={
                    "hostel_id": str(room.hostel_id),
                    "bed_status": BedStatus.AVAILABLE,
                    "monthly_price": room.monthly_price,
                },
            )
            beds.append(bed)
    return beds


def seed_users(db: Session, hostels):
    # Superadmin
    superadmin, _ = get_or_create(
        db,
        User,
        username="superadmin",   # 🔑 match on username, not email
        defaults={
            "email": "superadmin@example.com",   # will be ignored if row already exists
            "phone_number": "9999999999",
            "country_code": "+91",
            "hashed_password": get_password_hash("superadmin123"),
            "full_name": "Super Admin",
            "name": "Super Admin",
            "role": Role.SUPERADMIN.value,
            "is_active": True,
            "is_email_verified": True,
            "is_phone_verified": True,
        },
    )

    admin, _ = get_or_create(
        db,
        User,
        email="admin@example.com",
        defaults={
            "phone_number": "8888888888",
            "country_code": "+91",
            "username": "admin1",
            "hashed_password": get_password_hash("admin123"),
            "full_name": "Hostel Admin",
            "name": "Hostel Admin",
            "role": Role.ADMIN.value,
            "hostel_id": hostels[0].id,
            "is_active": True,
            "is_email_verified": True,
            "is_phone_verified": True,
        },
    )

    supervisor, _ = get_or_create(
        db,
        User,
        email="supervisor@example.com",
        defaults={
            "phone_number": "7777777777",
            "country_code": "+91",
            "username": "supervisor1",
            "hashed_password": get_password_hash("supervisor123"),
            "full_name": "Hostel Supervisor",
            "name": "Hostel Supervisor",
            "role": Role.SUPERVISOR.value,
            "hostel_id": hostels[0].id,
            "is_active": True,
            "is_email_verified": True,
            "is_phone_verified": True,
        },
    )

    student, _ = get_or_create(
        db,
        User,
        email="student@example.com",
        defaults={
            "phone_number": "6666666666",
            "country_code": "+91",
            "username": "student1",
            "hashed_password": get_password_hash("student123"),
            "full_name": "Test Student",
            "name": "Test Student",
            "role": Role.STUDENT.value,
            "hostel_id": hostels[0].id,
            "is_active": True,
            "is_email_verified": True,
            "is_phone_verified": True,
        },
    )

    visitor, _ = get_or_create(
        db,
        User,
        email="visitor@example.com",
        defaults={
            "phone_number": "5555555555",
            "country_code": "+91",
            "username": "visitor1",
            "hashed_password": get_password_hash("visitor123"),
            "full_name": "Site Visitor",
            "name": "Site Visitor",
            "role": Role.VISITOR.value,
            "is_active": True,
            "is_email_verified": True,
            "is_phone_verified": True,
        },
    )

    return {
        "superadmin": superadmin,
        "admin": admin,
        "supervisor": supervisor,
        "student": student,
        "visitor": visitor,
    }


def seed_admin_and_assignments(db: Session, users, hostels):
    admin_user = users["admin"]

    admin_entity, _ = get_or_create(
        db,
        Admin,
        email=admin_user.email,
        defaults={
            "admin_name": admin_user.full_name or admin_user.username,
            "is_active": True,
        },
    )

    assignment, _ = get_or_create(
        db,
        AdminHostelAssignment,
        admin_id=admin_entity.id,
        hostel_id=hostels[0].id,
        defaults={"permission_level": PermissionLevel.admin},
    )

    return admin_entity, assignment


def seed_students(db: Session, hostels):
    s1, _ = get_or_create(
        db,
        Student,
        student_id="STU001",
        defaults={
            "student_name": "Alice Student",
            "student_email": "alicestu@example.com",
            "student_phone": "9000000001",
            "status": "active",
            "room_assignment": "101",
            "bed_assignment": "101-1",
        },
    )
    s2, _ = get_or_create(
        db,
        Student,
        student_id="STU002",
        defaults={
            "student_name": "Bob Student",
            "student_email": "bobstu@example.com",
            "student_phone": "9000000002",
            "status": "active",
        },
    )
    return [s1, s2]


def seed_student_payments_attendance_docs(db: Session, students):
    today = date.today()

    for s in students:
        # Payment
        sp, _ = get_or_create(
            db,
            StudentPayment,
            student_id=s.student_id,
            transaction_id=f"SPAY-{s.student_id}",
            defaults={
                "payment_type": StudentPaymentType.RENT,
                "amount": 5000.0,
                "payment_method": StudentPaymentMethod.CASH,
                "payment_date": today,
                "due_date": today,
                "status": "paid",
            },
        )
        # Attendance
        sa, _ = get_or_create(
            db,
            StudentAttendance,
            student_id=s.student_id,
            attendance_date=today,
            defaults={
                "attendance_mode": StudentAttendanceMode.IN_PERSON,
                "status": "present",
            },
        )
        # Document
        sd, _ = get_or_create(
            db,
            StudentDocument,
            student_id=s.student_id,
            doc_url=f"/uploads/docs/{s.student_id}_id.pdf",
            defaults={
                "doc_type": "id_proof",
            },
        )


def seed_supervisors(db: Session, hostels):
    sup, _ = get_or_create(
        db,
        Supervisor,
        employee_id="EMP001",
        defaults={
            "supervisor_name": "Ops Supervisor",
            "supervisor_email": "ops.supervisor@example.com",
            "supervisor_phone": "9100000000",
            "role": SupervisorRole.SUPERVISOR,
            "department": Department.OPERATIONS,
            "access_level": AccessLevel.FULL,
            "status": "active",
        },
    )

    sh, _ = get_or_create(
        db,
        SupervisorHostel,
        employee_id="EMP001",
        hostel_id=str(hostels[0].id),
        defaults={},
    )

    sa, _ = get_or_create(
        db,
        SupervisorActivity,
        employee_id="EMP001",
        action="login",
        defaults={
            "details": "Initial login",
        },
    )

    ao, _ = get_or_create(
        db,
        AdminOverride,
        admin_employee_id="EMP001",
        target_supervisor_id="EMP001",
        action="assign_hostel",
        defaults={
            "details": f"Assigned hostel {hostels[0].id}",
        },
    )

    return sup


def seed_fee_structure(db: Session, hostels):
    fp1, _ = get_or_create(
        db,
        FeePlan,
        hostel_id=hostels[0].id,
        plan_name="Standard Monthly",
        defaults={
            "frequency": FeeFrequency.monthly,
            "amount": 8000.0,
            "room_type": "single",
            "description": "Standard monthly single room plan",
        },
    )
    sd1, _ = get_or_create(
        db,
        SecurityDeposit,
        hostel_id=hostels[0].id,
        name="Security Deposit",
        defaults={"amount": 5000.0, "refundable": True},
    )
    mc1, _ = get_or_create(
        db,
        MessCharge,
        hostel_id=hostels[0].id,
        meal_type="full_mess",
        defaults={
            "frequency": FeeFrequency.monthly,
            "amount": 2500.0,
            "is_mandatory": True,
        },
    )
    as1, _ = get_or_create(
        db,
        AdditionalService,
        hostel_id=hostels[0].id,
        service_name="Laundry",
        defaults={"amount": 500.0, "frequency": FeeFrequency.monthly},
    )
    return [fp1, sd1, mc1, as1]


def seed_subscription_system(db: Session, hostels):
    plan, _ = get_or_create(
        db,
        SubscriptionPlan,
        name="Pro Plan",
        tier=PlanTier.premium,
        billing_cycle=BillingCycle.monthly,
        defaults={
            "price": Decimal("199.99"),
            "currency": "USD",
            "max_hostels": 10,
            "max_admins": 20,
            "max_students": 1000,
            "features": {"reports": True, "priority_support": True},
        },
    )

    sub, _ = get_or_create(
        db,
        Subscription,
        organization_id="ORG001",
        defaults={
            "organization_name": "Demo Organization",
            "email": "billing@demo.org",
            "plan_id": plan.id,
            "status": SubscriptionStatus.active,
            "current_period_start": datetime.utcnow() - timedelta(days=5),
            "current_period_end": datetime.utcnow() + timedelta(days=25),
        },
    )

    pay, _ = get_or_create(
        db,
        SubPayment,
        id=f"pay_{sub.id}",
        defaults={
            "subscription_id": sub.id,
            "hostel_id": hostels[0].id,
            "amount": Decimal("199.99"),
            "currency": "USD",
            "status": SubPaymentStatus.succeeded,
            "payment_type": SubPaymentType.subscription,
            "payment_method": "card",
        },
    )

    chg, _ = get_or_create(
        db,
        SubscriptionChange,
        subscription_id=sub.id,
        change_type=ChangeType.upgrade,
        effective_date=datetime.utcnow(),
        initiated_by="superadmin",
        defaults={
            "from_plan_id": plan.id,
            "to_plan_id": plan.id,
            "proration_amount": Decimal("0.00"),
        },
    )

    return plan, sub, pay, chg


def seed_invoices_transactions_receipts_refunds(db: Session, users, hostels):
    student = users["student"]
    today = datetime.utcnow()

    # 1️⃣ Ensure we have a real Payment (subscription.Payment) row to link to
    pay_obj = db.query(SubPayment).first()
    if not pay_obj:
        # If none exists (e.g. subscription seeding was skipped), create a minimal one
        pay_obj = SubPayment(
            # id will be auto-generated by model's default if not provided
            subscription_id=None,
            user_id=student.id,
            hostel_id=hostels[0].id,
            amount=Decimal("4000.00"),
            currency="INR",
            status=SubPaymentStatus.succeeded,
            payment_type=SubPaymentType.subscription,
            payment_method="cash",
            description="Seeded payment for invoice",
            notes="Created automatically by seed_invoices_transactions_receipts_refunds",
        )
        db.add(pay_obj)
        db.commit()
        db.refresh(pay_obj)

    # 2️⃣ Create or get an Invoice
    invoice, created = get_or_create(
        db,
        Invoice,
        invoice_number="INV-TEST-001",
        defaults={
            "user_id": student.id,
            "hostel_id": hostels[0].id,
            "total_amount": 8000.0,
            "paid_amount": 0.0,
            "due_amount": 8000.0,
            "description": "Initial hostel fee invoice",
            "items": '[{"description": "Hostel Fee", "quantity": 1, "unit_price": 8000, "amount": 8000}]',
            "status": PaymentStatus.PENDING.value,
            "issue_date": today,
            "due_date": today + timedelta(days=7),
        },
    )

    if created:
        # 3️⃣ Create a Transaction linked to the real Payment
        txn = Transaction(
            transaction_id="TXN-TEST-001",
            payment_id=pay_obj.id,           # ✅ use existing Payment.id
            invoice_id=invoice.id,
            transaction_type=TransactionType.PAYMENT,
            amount=4000.0,
            payment_method="cash",
            payment_gateway=None,
            gateway_transaction_id=None,
            notes=None,
            status="success",
            processed_by=None,
            created_at=today,
        )
        db.add(txn)

        # 4️⃣ Update invoice amounts and status
        invoice.paid_amount = 4000.0
        invoice.due_amount = 4000.0
        invoice.status = PaymentStatus.PENDING.value
        db.commit()
        db.refresh(invoice)
        db.refresh(txn)

        # 5️⃣ Create a Receipt
        receipt = Receipt(
            receipt_number="RCP-TEST-001",
            invoice_id=invoice.id,
            transaction_id=txn.id,
            payment_id=pay_obj.id,
            amount=txn.amount,
            qr_code_data="demo-qr-data",
            generated_at=today,
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        # 6️⃣ Seed a RefundRequest linked to the same invoice/transaction
        refund_req = RefundRequest(
            refund_id="RFN-TEST-001",
            transaction_id=txn.id,
            invoice_id=invoice.id,
            refund_amount=1000.0,
            reason="Test partial refund",
            status="initiated",
            requested_by=student.id,
        )
        db.add(refund_req)
        db.commit()

    # Webhook & Refund tables
    cust, _ = get_or_create(
        db,
        Customer,
        email="customer@example.com",
        defaults={
            "name": "Payment Customer",
            "phone": "9123456789",
        },
    )

    wh, _ = get_or_create(
        db,
        PaymentWebhook,
        id=1,
        defaults={
            "gateway": "razorpay",
            "event_type": "payment.captured",
            "payload": '{"dummy": "payload"}',
            "payment_id": "pay_test_123",
            "order_id": "order_test_123",
        },
    )

    ref, _ = get_or_create(
        db,
        Refund,
        refund_id="GW_REFUND_001",
        defaults={
            "payment_id": "pay_test_123",
            "amount": 500.0,
            "status": "completed",
        },
    )

    return invoice


def seed_reminder_system(db: Session, hostels, invoices):
    cfg, _ = get_or_create(
        db,
        ReminderConfiguration,
        hostel_id=hostels[0].id,
        defaults={
            "pre_due_days": "7,3,1",
            "pre_due_channels": ReminderChannel.EMAIL,
            "due_date_enabled": True,
            "due_date_channels": ReminderChannel.BOTH,
            "overdue_frequency_days": 3,
            "overdue_channels": ReminderChannel.BOTH,
            "escalation_enabled": True,
            "escalation_1_days": 7,
            "escalation_2_days": 14,
            "escalation_3_days": 30,
            "final_notice_days": 45,
            "max_reminders": 10,
        },
    )

    inv = invoices

    pr, _ = get_or_create(
        db,
        PaymentReminder,
        reminder_id="REM-TEST-001",
        defaults={
            "invoice_id": inv.id,
            "reminder_type": ReminderType.PRE_DUE,
            "channel": ReminderChannel.EMAIL,
            "recipient_email": "student@example.com",
            "subject": "Payment reminder",
            "message_body": "Please pay your hostel fee.",
            "status": ReminderStatus.SENT,
            "scheduled_at": datetime.utcnow(),
        },
    )

    tmpl, _ = get_or_create(
        db,
        ReminderTemplate,
        name="Default Pre-Due Template",
        reminder_type=ReminderType.PRE_DUE,
        defaults={
            "email_subject": "Your hostel payment is due soon",
            "email_body": "Dear {{user_name}}, your payment is due.",
            "sms_body": "Your hostel payment is due soon.",
            "is_default": True,
        },
    )

    return cfg, pr, tmpl


def seed_waitlist_and_bookings(db: Session, hostels, rooms, users):
    # Waitlist
    wl1, _ = get_or_create(
        db,
        Waitlist,
        hostel_id=hostels[0].id,
        room_type="single",
        visitor_id=users["visitor"].id,
        defaults={
            "priority": 1,
            "created_at": datetime.utcnow(),
        },
    )

    # Booking
    b1, _ = get_or_create(
        db,
        Booking,
        id=1,
        defaults={
            "visitor_id": users["visitor"].id,
            "hostel_id": hostels[0].id,
            "room_id": rooms[0].id,
            "check_in": datetime.utcnow() + timedelta(days=2),
            "check_out": datetime.utcnow() + timedelta(days=10),
            "amount_paid": 2000.0,
            "status": BookingStatus.confirmed.value,
            "created_at": datetime.utcnow(),
        },
    )

    return wl1, b1


def seed_mess_menu_system(db: Session, hostels, users):
    menu, _ = get_or_create(
        db,
        MessMenu,
        id=1,
        defaults={
            "hostel_id": hostels[0].id,
            "menu_type": MenuType.DAILY,
            "menu_date": date.today(),
            "meal_type": MealType.LUNCH,
            "items": [{"name": "Rice", "description": "Plain rice"}],
            "diet_types": ["regular"],
            "status": MenuStatus.PUBLISHED,
            "created_by": users["admin"].id,
            "created_by_role": users["admin"].role,
        },
    )

    fb, _ = get_or_create(
        db,
        MenuFeedback,
        menu_id=menu.id,
        student_id=1,
        defaults={
            "rating": 4,
            "taste_rating": 4,
            "quantity_rating": 4,
            "hygiene_rating": 4,
            "comments": "Good food",
        },
    )

    pref, _ = get_or_create(
        db,
        MealPreference,
        student_id=1,
        hostel_id=hostels[0].id,
        defaults={
            "diet_type": DietType.VEGETARIAN,
            "allergies": ["nuts"],
            "preferred_items": ["Paneer"],
            "disliked_items": ["Brinjal"],
            "is_active": True,
        },
    )

    return menu


def seed_announcements(db: Session, users):
    ann, _ = get_or_create(
        db,
        Announcement,
        id=1,
        defaults={
            "announcement_title": "Welcome Notice",
            "announcement_content": "Welcome to the hostel management system.",
            "announcement_category": AnnouncementCategory.GENERAL.value,
            "target_audience": "all",
            "is_emergency": False,
            "status": AnnouncementStatus.PUBLISHED.value,
            "created_by_id": users["admin"].id,
            "approved": True,
        },
    )
    return ann


def seed_reports_data(db: Session, hostels, users):
    today = date.today()
    # Attendance report-level
    ra, _ = get_or_create(
        db,
        ReportAttendance,
        hostel_id=hostels[0].id,
        student_id=1,
        date=today,
        defaults={
            "student_name": "Alice Student",
            "is_present": True,
        },
    )

    ft, _ = get_or_create(
        db,
        FinancialTransaction,
        hostel_id=hostels[0].id,
        student_id=1,
        transaction_type="fee",
        category="hostel_fee",
        transaction_date=today,
        defaults={
            "amount": Decimal("8000.00"),
            "payment_status": "pending",
        },
    )

    hb, _ = get_or_create(
        db,
        HostelBooking,
        hostel_id=hostels[0].id,
        student_name="Alice Student",
        defaults={
            "student_email": "alicestu@example.com",
            "room_type": "single",
            "converted": True,
        },
    )

    hpv, _ = get_or_create(
        db,
        HostelProfileView,
        hostel_id=hostels[0].id,
        session_id="sess1",
        defaults={
            "visitor_ip": "127.0.0.1",
            "source": "search",
        },
    )

    sq, _ = get_or_create(
        db,
        SearchQuery,
        id=1,
        defaults={
            "query_text": "hostel hyderabad",
            "city": "Hyderabad",
            "filters": '{"gender": "Boys"}',
            "results_count": 3,
        },
    )


def seed_report_models(db: Session, hostels, users):
    # Booking report + commission
    br, _ = get_or_create(
        db,
        BookingReport,
        id="book_test_1",
        defaults={
            "hostel_id": str(hostels[0].id),
            "hostel_name": hostels[0].hostel_name,
            "user_id": str(users["visitor"].id),
            "user_name": users["visitor"].name,
            "room_type": "single",
            "check_in_date": datetime.utcnow(),
            "check_out_date": datetime.utcnow() + timedelta(days=5),
            "amount": Decimal("5000.00"),
            "commission_rate": Decimal("0.15"),
            "commission_amount": Decimal("750.00"),
            "status": ReportBookingStatus.CONFIRMED,
            "payment_status": ReportPaymentStatus.PAID,
        },
    )

    comm, _ = get_or_create(
        db,
        Commission,
        booking_id=br.id,
        defaults={
            "amount": br.commission_amount,
            "status": CommissionStatus.PENDING,
            "earned_date": datetime.utcnow(),
            "hostel_id": str(hostels[0].id),
            "platform_revenue": br.commission_amount,
        },
    )

    sr, _ = get_or_create(
        db,
        SubscriptionRevenue,
        id="subrev_1",
        defaults={
            "subscription_id": "sub_1",
            "organization_id": "ORG001",
            "organization_name": "Demo Organization",
            "amount": Decimal("199.99"),
            "plan_name": "Pro Plan",
            "billing_date": datetime.utcnow(),
            "period_start": datetime.utcnow() - timedelta(days=30),
            "period_end": datetime.utcnow(),
        },
    )

    fr, _ = get_or_create(
        db,
        FinancialSummary,
        id="finsum_1",
        defaults={
            "period_start": datetime.utcnow() - timedelta(days=30),
            "period_end": datetime.utcnow(),
            "total_income": Decimal("100000.00"),
            "subscription_revenue": Decimal("199.99"),
            "commission_earned": Decimal("750.00"),
            "pending_payments": Decimal("1000.00"),
            "total_bookings": 10,
            "completed_bookings": 8,
            "cancelled_bookings": 2,
        },
    )

    rep, _ = get_or_create(
        db,
        Report,
        id="rep_1",
        defaults={
            "name": "Demo Revenue Report",
            "report_type": ReportType.REVENUE,
            "start_date": datetime.utcnow() - timedelta(days=30),
            "end_date": datetime.utcnow(),
            "parameters": {"type": "revenue"},
            "result_data": {
                "summary": {
                    "total_income": "100000.00",
                    "subscription_revenue": "199.99",
                },
                "by_hostel": [],
            },
            "export_format": ExportFormat.PDF,
            "generated_by": "superadmin",
            "generated_at": datetime.utcnow(),
        },
    )


def seed_notifications(db: Session, users):
    tmpl, _ = get_or_create(
        db,
        NotificationTemplate,
        name="welcome_email",
        defaults={
            "channel": "email",
            "subject_template": "Welcome, {{name}}",
            "body_template": "Hello {{name}}, welcome to {{app_name}}",
        },
    )

    notif, _ = get_or_create(
        db,
        Notification,
        id=1,
        defaults={
            "recipient_id": users["student"].email,
            "recipient_type": "student",
            "channel": Channel.EMAIL.value,
            "subject": "Welcome to Hostel",
            "body": "Your registration is complete.",
            "template_id": tmpl.id,
            "sent": False,
        },
    )

    dev, _ = get_or_create(
        db,
        DeviceToken,
        user_id=str(users["student"].id),
        token="fcm_device_token",
        defaults={
            "platform": "android",
        },
    )


def seed_session_context(db: Session, users, hostels):
    admin = users["admin"]
    sc, _ = get_or_create(
        db,
        SessionContext,
        user_id=admin.id,
        hostel_id=hostels[0].id,
        defaults={"is_active": True},
    )
    return sc


# ---------------------------------------------------------
# Orchestration
# ---------------------------------------------------------

def run():
    print("🚀 Seeding ALL core data...")
    # Make sure tables exist
    init_db()

    db = SessionLocal()
    try:
        locations = seed_locations(db)
        print("✔ Locations")

        hostels = seed_hostels(db, locations)
        print("✔ Hostels")

        rooms = seed_rooms(db, hostels)
        print(f"✔ Rooms ({len(rooms)})")

        beds = seed_beds(db, rooms)
        print(f"✔ Beds ({len(beds)})")

        users = seed_users(db, hostels)
        print("✔ Users (superadmin/admin/supervisor/student/visitor)")

        admin_entity, aha = seed_admin_and_assignments(db, users, hostels)
        print("✔ Admin entity & hostel assignment")

        students = seed_students(db, hostels)
        seed_student_payments_attendance_docs(db, students)
        print("✔ Students + their payments/attendance/documents")

        sup = seed_supervisors(db, hostels)
        print("✔ Supervisors & supervisor-hostel/activity/admin-overrides")

        fee_items = seed_fee_structure(db, hostels)
        print("✔ Fee structure (plans/deposits/mess/additional services)")

        sub_plan, sub, sub_pay, sub_chg = seed_subscription_system(db, hostels)
        print("✔ Subscription system (plan/subscription/payment/change)")

        invoice = seed_invoices_transactions_receipts_refunds(db, users, hostels)
        print("✔ Invoices, transactions, receipts, refund_requests, payment webhooks, refunds")

        cfg, pay_rem, tmpl = seed_reminder_system(db, hostels, invoice)
        print("✔ Reminder config, payment reminders, reminder templates")

        wl, booking = seed_waitlist_and_bookings(db, hostels, rooms, users)
        print("✔ Waitlist & basic bookings")

        menu = seed_mess_menu_system(db, hostels, users)
        print("✔ Mess menu, feedback, preferences")

        ann = seed_announcements(db, users)
        print("✔ Announcements")

        seed_reports_data(db, hostels, users)
        print("✔ Report base tables (attendance, financial txns, bookings, views, search queries)")

        seed_report_models(db, hostels, users)
        print("✔ Report models (booking reports, commissions, subscription revenues, financial summaries, reports)")

        seed_notifications(db, users)
        print("✔ Notification templates, notifications, device tokens")

        sc = seed_session_context(db, users, hostels)
        print("✔ Session context")

        print("🎉 Seeding COMPLETED.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
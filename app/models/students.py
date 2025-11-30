from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, Date, Time, Boolean, func, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.schema import Identity
from sqlalchemy.orm import relationship

from app.config import Base


class PaymentStatus(str, Enum):
    PAID = "paid"
    PENDING = "pending"
    FAILED = "failed"


class PaymentType(str, Enum):
    RENT = "rent"
    DEPOSIT = "deposit"
    MAINTENANCE = "maintenance"
    UTILITY = "utility"
    LATE_FEE = "late_fee"
    OTHER = "other"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CHECK = "check"
    OTHER = "other"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"


class AttendanceMode(str, Enum):
    IN_PERSON = "in_person"
    REMOTE = "remote"
    HYBRID = "hybrid"
    LEAVE = "leave"


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String, primary_key=True, index=True)
    student_name = Column(String, nullable=False)
    student_email = Column(String, unique=True, nullable=False)
    student_phone = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    guardian_name = Column(String, nullable=True)
    guardian_phone = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    check_in_date = Column(Date, nullable=True)
    check_out_date = Column(Date, nullable=True)
    # legacy human readable assignment fields (kept for backwards compatibility)
    room_assignment = Column(String, nullable=True)
    bed_assignment = Column(String, nullable=True)

    # Proper foreign-key relationships to rooms and beds
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=True)
    status = Column(String, nullable=True)

    # New relationships/fields
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    hostel = relationship("Hostel", back_populates="students")

    # relationships to room/bed (use the explicit foreign keys above)
    room = relationship("Room", back_populates="students")
    bed = relationship("Bed", back_populates="students")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=True)
    user = relationship("User", back_populates="student")



class StudentStatusHistory(Base):
    """History log for student status changes and transfers."""
    __tablename__ = "student_status_history"

    id = Column(Integer, Identity(start=1), primary_key=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False, index=True)
    event_type = Column(String, nullable=False)  # 'status_change' or 'transfer'
    old_status = Column(String, nullable=True)
    new_status = Column(String, nullable=True)
    old_room = Column(String, nullable=True)
    old_bed = Column(String, nullable=True)
    new_room = Column(String, nullable=True)
    new_bed = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class StudentPayment(Base):
    __tablename__ = "student_payments"

    id = Column(Integer, Identity(start=1), primary_key=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False, index=True)
    payment_type = Column(SAEnum(PaymentType, name="payment_type_enum"), nullable=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(SAEnum(PaymentMethod, name="payment_method_enum"), nullable=True)
    payment_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    transaction_id = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    status = Column(String, nullable=False)  # use PaymentStatus values
    method = Column(String, nullable=True)  # kept for backward compatibility
    paid_at = Column(DateTime(timezone=True), nullable=True)  # kept for backward compatibility
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Attendance(Base):
    __tablename__ = "student_attendance"

    id = Column(Integer, Identity(start=1), primary_key=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False)
    attendance_mode = Column(SAEnum(AttendanceMode, name="attendance_mode_enum"), nullable=True)
    check_in_time = Column(Time, nullable=True)
    check_out_time = Column(Time, nullable=True)
    is_late = Column(Boolean, nullable=True, default=False)
    date = Column(Date, nullable=True)  # kept for backward compatibility
    status = Column(String, nullable=False)  # use AttendanceStatus values
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class StudentDocument(Base):
    __tablename__ = "student_documents"

    id = Column(Integer, Identity(start=1), primary_key=True)
    student_id = Column(String, ForeignKey("students.student_id"), nullable=False, index=True)
    doc_type = Column(String, nullable=True)
    doc_url = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

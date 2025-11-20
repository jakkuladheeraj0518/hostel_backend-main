from __future__ import annotations
from typing import Optional
from datetime import date, datetime, time
from pydantic import BaseModel, EmailStr
from app.models.students import (
    PaymentType, PaymentMethod, AttendanceMode
)

# STUDENT SCHEMAS

class StudentBase(BaseModel):
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    student_email: Optional[EmailStr] = None
    student_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    room_assignment: Optional[str] = None
    bed_assignment: Optional[str] = None
    status: Optional[str] = None


class StudentCreate(StudentBase):
    student_id: str
    student_name: str
    student_email: EmailStr
    student_phone: str


class StudentUpdate(BaseModel):
    student_name: Optional[str] = None
    student_email: Optional[EmailStr] = None
    student_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    guardian_name: Optional[str] = None
    guardian_phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    check_in_date: Optional[date] = None
    room_assignment: Optional[str] = None
    bed_assignment: Optional[str] = None
    status: Optional[str] = None


class StudentOut(StudentBase):
    student_id: str

    class Config:
        from_attributes = True


# PAYMENT SCHEMAS

class PaymentBase(BaseModel):
    payment_type: PaymentType
    amount: float
    payment_method: PaymentMethod
    payment_date: date
    due_date: date
    transaction_id: str
    notes: Optional[str] = None
    status: str


class PaymentCreate(PaymentBase):
    student_name: Optional[str] = None  # Optional, student_id comes from path


class PaymentOut(PaymentBase):
    id: int
    student_id: str
    student_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ATTENDANCE SCHEMAS

class AttendanceBase(BaseModel):
    attendance_date: date
    attendance_mode: AttendanceMode
    check_in_time: time
    check_out_time: time
    is_late: bool
    notes: Optional[str] = None
    status: str


class AttendanceCreate(AttendanceBase):
    student_name: Optional[str] = None  # Optional, student_id comes from path


class AttendanceOut(AttendanceBase):
    id: int
    student_id: str
    student_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# STUDENT DOCUMENT SCHEMAS

class StudentDocumentCreate(BaseModel):
    doc_type: Optional[str] = None
    doc_url: str


class StudentDocumentOut(StudentDocumentCreate):
    id: int
    student_id: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

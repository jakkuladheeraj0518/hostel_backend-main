from typing import List, Optional
from datetime import date, datetime, time as time_type
from sqlalchemy.orm import Session
from app.repositories.student_repository import (
    list_students as repo_list_students,
    get_student as repo_get_student,
    create_student as repo_create_student,
    update_student as repo_update_student,
    delete_student as repo_delete_student,
    set_status as repo_set_status,
    transfer as repo_transfer,
    list_history as repo_list_history,
    create_payment as repo_create_payment,
    list_payments as repo_list_payments,
    create_attendance as repo_create_attendance,
    list_attendance as repo_list_attendance,
    create_student_document as repo_create_student_document,
    list_student_documents as repo_list_student_documents,
)
from app.schemas.students import (
    StudentCreate,
    StudentOut,
    StudentUpdate,
    StudentDocumentCreate,
    StudentDocumentOut,
    PaymentOut,
    PaymentCreate,
    AttendanceOut,
    AttendanceCreate,
)
from app.models.students import PaymentType, PaymentMethod, AttendanceMode


# ---- Student CRUD / status / transfer ----

def list_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    room: Optional[str] = None,
    payment_status: Optional[str] = None,
    attendance_status: Optional[str] = None,
) -> List:
    return repo_list_students(
        db,
        skip=skip,
        limit=limit,
        name=name,
        room=room,
        payment_status=payment_status,
        attendance_status=attendance_status,
    )


def get_student(db: Session, student_id: str):
    return repo_get_student(db, student_id)


def create_student(db: Session, student_in: StudentCreate):
    return repo_create_student(db, student_in)


def update_student(db: Session, student_id: str, student_in: StudentUpdate):
    return repo_update_student(db, student_id, student_in)


def delete_student(db: Session, student_id: str) -> bool:
    return repo_delete_student(db, student_id)


def set_student_status(db: Session, student_id: str, new_status: str, notes: Optional[str] = None):
    return repo_set_status(db, student_id, new_status, notes)


def transfer_student(db: Session, student_id: str, new_room: Optional[str], new_bed: Optional[str], notes: Optional[str] = None):
    return repo_transfer(db, student_id, new_room, new_bed, notes)


def get_student_history(db: Session, student_id: str) -> List[dict]:
    return repo_list_history(db, student_id)


# ---- Payments / mapper ----

def _payment_to_payment_out(db: Session, payment) -> PaymentOut:
    """
    Normalize Payment model -> PaymentOut (resolving student name and enums).
    Falls back to reasonable defaults when fields missing.
    """
    student = repo_get_student(db, payment.student_id)
    student_name = student.student_name if student else ""

    # Convert or fallback payment_type / method to enums expected by Pydantic
    payment_type = PaymentType.OTHER
    if payment.payment_type:
        try:
            payment_type = PaymentType(payment.payment_type) if not isinstance(payment.payment_type, PaymentType) else payment.payment_type
        except Exception:
            payment_type = PaymentType.OTHER

    payment_method = PaymentMethod.OTHER
    if payment.payment_method:
        try:
            payment_method = PaymentMethod(payment.payment_method) if not isinstance(payment.payment_method, PaymentMethod) else payment.payment_method
        except Exception:
            payment_method = PaymentMethod.OTHER

    # Determine payment_date
    pay_date = payment.payment_date
    if not pay_date and getattr(payment, "paid_at", None):
        pay_date = payment.paid_at.date()

    # fallback to today if absolutely missing
    if not pay_date:
        pay_date = date.today()

    return PaymentOut(
        id=payment.id,
        student_id=payment.student_id,
        student_name=student_name,
        payment_type=payment_type,
        amount=payment.amount,
        payment_method=payment_method,
        payment_date=pay_date,
        due_date=payment.due_date or pay_date,
        transaction_id=payment.transaction_id or "",
        status=payment.status,
        notes=payment.notes,
        created_at=payment.created_at,
    )


def create_payment(db: Session, student_id: str, payload: PaymentCreate) -> PaymentOut:
    payment = repo_create_payment(
        db=db,
        student_id=student_id,
        payment_type=payload.payment_type.value if payload.payment_type else None,
        amount=payload.amount,
        payment_method=payload.payment_method.value if payload.payment_method else None,
        payment_date=payload.payment_date,
        due_date=payload.due_date,
        transaction_id=payload.transaction_id,
        status=payload.status,
        notes=payload.notes,
    )
    return _payment_to_payment_out(db, payment)


def list_payments(db: Session, student_id: str) -> List[PaymentOut]:
    payments = repo_list_payments(db, student_id)
    return [_payment_to_payment_out(db, p) for p in payments]


# ---- Attendance / mapper ----

def _attendance_to_attendance_out(db: Session, attendance) -> AttendanceOut:
    student = repo_get_student(db, attendance.student_id)
    student_name = student.student_name if student else ""

    attendance_mode = AttendanceMode.IN_PERSON
    if attendance.attendance_mode:
        try:
            attendance_mode = AttendanceMode(attendance.attendance_mode) if not isinstance(attendance.attendance_mode, AttendanceMode) else attendance.attendance_mode
        except Exception:
            attendance_mode = AttendanceMode.IN_PERSON

    attendance_date = attendance.attendance_date or getattr(attendance, "date", None)
    if not attendance_date:
        from datetime import date
        attendance_date = date.today()

    check_in_time = attendance.check_in_time or time_type(9, 0)
    check_out_time = attendance.check_out_time or time_type(17, 0)

    return AttendanceOut(
        id=attendance.id,
        student_id=attendance.student_id,
        student_name=student_name,
        attendance_date=attendance_date,
        attendance_mode=attendance_mode,
        check_in_time=check_in_time,
        check_out_time=check_out_time,
        is_late=attendance.is_late if attendance.is_late is not None else False,
        status=attendance.status,
        notes=attendance.notes,
        created_at=attendance.created_at,
    )


def create_attendance(db: Session, student_id: str, payload: AttendanceCreate) -> AttendanceOut:
    attendance = repo_create_attendance(
        db=db,
        student_id=student_id,
        attendance_date=payload.attendance_date,
        attendance_mode=payload.attendance_mode.value if payload.attendance_mode else None,
        check_in_time=payload.check_in_time,
        check_out_time=payload.check_out_time,
        is_late=payload.is_late,
        status=payload.status,
        notes=payload.notes,
    )
    return _attendance_to_attendance_out(db, attendance)


def list_attendance(db: Session, student_id: str) -> List[AttendanceOut]:
    attendances = repo_list_attendance(db, student_id)
    return [_attendance_to_attendance_out(db, a) for a in attendances]


# ---- Student Documents ----

def create_student_document(db: Session, student_id: str, payload: StudentDocumentCreate):
    return repo_create_student_document(db, student_id, payload.doc_type, payload.doc_url)


def list_student_documents(db: Session, student_id: str):
    return repo_list_student_documents(db, student_id)

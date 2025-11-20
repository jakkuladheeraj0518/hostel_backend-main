from typing import List, Optional
from datetime import date, datetime, time
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.models.students import Student, StudentPayment, Attendance, StudentDocument
from app.schemas.students import StudentCreate, StudentUpdate


def list_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    room: Optional[str] = None,
    payment_status: Optional[str] = None,
    attendance_status: Optional[str] = None,
) -> List[Student]:
    query = db.query(Student)
    
    if name:
        query = query.filter(Student.student_name.ilike(f"%{name}%"))
    if room:
        query = query.filter(Student.room_assignment == room)
    if payment_status:
        query = query.filter(
            db.query(StudentPayment.id)
              .filter(StudentPayment.student_id == Student.student_id, StudentPayment.status == payment_status)
              .exists()
        )
    if attendance_status:
        query = query.filter(
            db.query(Attendance.id)
              .filter(Attendance.student_id == Student.student_id, Attendance.status == attendance_status)
              .exists()
        )

    return query.order_by(Student.student_id).offset(skip).limit(limit).all()


def get_student(db: Session, student_id: str) -> Optional[Student]:
    return db.query(Student).filter(Student.student_id == student_id).first()


def create_student(db: Session, student_in: StudentCreate) -> Student:
    obj = Student(**student_in.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_student(db: Session, student_id: str, student_in: StudentUpdate) -> Optional[Student]:
    obj = get_student(db, student_id)
    if not obj:
        return None
    
    for field, value in student_in.dict(exclude_unset=True).items():
        setattr(obj, field, value)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete_student(db: Session, student_id: str) -> bool:
    obj = get_student(db, student_id)
    if not obj:
        return False

    db.delete(obj)
    db.commit()
    return True


def set_status(db: Session, student_id: str, new_status: str, notes: Optional[str] = None) -> Optional[Student]:
    obj = get_student(db, student_id)
    if not obj:
        return None

    old_status = obj.status
    obj.status = new_status
    db.add(obj)
    db.commit()
    db.refresh(obj)

    db.execute(
        text("""
            INSERT INTO student_status_history (
                student_id, event_type, old_status, new_status, notes
            )
            VALUES (:sid, 'status_change', :old, :new, :notes)
        """),
        {
            "sid": student_id,
            "old": old_status,
            "new": new_status,
            "notes": notes or ""
        }
    )
    db.commit()

    return obj


def transfer(db: Session, student_id: str, new_room: Optional[str], new_bed: Optional[str], notes: Optional[str]) -> Optional[Student]:
    obj = get_student(db, student_id)
    if not obj:
        return None

    old_room = obj.room_assignment
    old_bed = obj.bed_assignment

    obj.room_assignment = new_room
    obj.bed_assignment = new_bed
    db.add(obj)
    db.commit()
    db.refresh(obj)

    db.execute(
        text("""
            INSERT INTO student_status_history (
                student_id, event_type, old_room, old_bed, new_room, new_bed, notes
            )
            VALUES (:sid, 'transfer', :old_room, :old_bed, :new_room, :new_bed, :notes)
        """),
        {
            "sid": student_id,
            "old_room": old_room,
            "old_bed": old_bed,
            "new_room": new_room,
            "new_bed": new_bed,
            "notes": notes or ""
        }
    )
    db.commit()

    return obj


def list_history(db: Session, student_id: str) -> List[dict]:
    rows = db.execute(
        text("""
            SELECT id, event_type, old_status, new_status, old_room, old_bed,
                   new_room, new_bed, notes, created_at
            FROM student_status_history
            WHERE student_id = :sid
            ORDER BY created_at DESC
        """),
        {"sid": student_id}
    )
    return [dict(r._mapping) for r in rows]


# ------- Payments -------

def create_payment(
    db: Session,
    student_id: str,
    payment_type: Optional[str],
    amount: float,
    payment_method: Optional[str],
    payment_date: Optional[date],
    due_date: Optional[date],
    transaction_id: Optional[str],
    status: str = "pending",
    notes: Optional[str] = None,
    currency: Optional[str] = None,
    method: Optional[str] = None,
    paid_at: Optional[datetime] = None,
) -> StudentPayment:
    p = StudentPayment(
        student_id=student_id,
        payment_type=payment_type,
        amount=amount,
        payment_method=payment_method,
        payment_date=payment_date,
        due_date=due_date,
        transaction_id=transaction_id,
        currency=currency,
        status=status,
        method=method,
        paid_at=paid_at,
        notes=notes
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def list_payments(db: Session, student_id: str) -> List[StudentPayment]:
    return db.query(StudentPayment).filter(
        StudentPayment.student_id == student_id
    ).order_by(StudentPayment.created_at.desc()).all()


# ------- Attendance -------

def create_attendance(
    db: Session,
    student_id: str,
    attendance_date: Optional[date],
    attendance_mode: Optional[str],
    check_in_time: Optional[time],
    check_out_time: Optional[time],
    is_late: bool,
    status: str,
    notes: Optional[str],
    date_val: Optional[date] = None,
) -> Attendance:

    final_date = attendance_date if attendance_date else date_val

    a = Attendance(
        student_id=student_id,
        attendance_date=final_date,
        attendance_mode=attendance_mode,
        check_in_time=check_in_time,
        check_out_time=check_out_time,
        is_late=is_late,
        date=final_date,
        status=status,
        notes=notes
    )

    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def list_attendance(db: Session, student_id: str) -> List[Attendance]:
    return db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).order_by(
        func.coalesce(Attendance.attendance_date, Attendance.date).desc()
    ).all()


# ------- Student Documents -------

def create_student_document(db: Session, student_id: str, doc_type: Optional[str], doc_url: str) -> StudentDocument:
    d = StudentDocument(student_id=student_id, doc_type=doc_type, doc_url=doc_url)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def list_student_documents(db: Session, student_id: str) -> List[StudentDocument]:
    return db.query(StudentDocument).filter(
        StudentDocument.student_id == student_id
    ).order_by(StudentDocument.uploaded_at.desc()).all()

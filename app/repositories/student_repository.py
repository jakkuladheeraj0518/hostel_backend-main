from typing import List, Optional
from datetime import date, datetime, time
from sqlalchemy.orm import Session
from sqlalchemy import text, func, or_
 
from app.models.students import Student, StudentPayment, Attendance, StudentDocument
from app.models.beds import Bed, BedStatus
from app.repositories.bed_repository import find_bed_by_room_and_bed_number
from app.schemas.students import StudentCreate, StudentUpdate
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate as SchemaUserCreate
from app.core.roles import Role as UserRole
 
 
def list_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    room: Optional[str] = None,
    payment_status: Optional[str] = None,
    attendance_status: Optional[str] = None,
    student_id: Optional[str] = None,
    student_email: Optional[str] = None,
    student_phone: Optional[str] = None,
    hostel_id: Optional[int] = None,
    bed: Optional[str] = None,
    status: Optional[str] = None,
    checkin_from: Optional[date] = None,
    checkin_to: Optional[date] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    payment_due_min: Optional[float] = None,
    payment_due_max: Optional[float] = None,
    attendance_pct_lt: Optional[float] = None,
    attendance_pct_gt: Optional[float] = None,
    complaint_count_lt: Optional[int] = None,
    complaint_count_gt: Optional[int] = None,
    user_hostel_ids: Optional[List[int]] = None,
    active_hostel_id: Optional[int] = None,
) -> List[Student]:
    query = db.query(Student)
   
    # Identity filters: treat name / id / email / phone as alternatives (OR)
    identity_filters = []
    if name:
        identity_filters.append(Student.student_name.ilike(f"%{name}%"))
    if student_id:
        identity_filters.append(Student.student_id.ilike(f"%{student_id}%"))
    if student_email:
        identity_filters.append(Student.student_email.ilike(f"%{student_email}%"))
    if student_phone:
        identity_filters.append(Student.student_phone.ilike(f"%{student_phone}%"))
    if identity_filters:
        query = query.filter(or_(*identity_filters))
    if room:
        # support numeric room ids as well as room_number strings
        try:
            room_id_val = int(room)
            query = query.filter(Student.room_id == room_id_val)
        except Exception:
            query = query.filter(Student.room_assignment == room)
    if bed:
        query = query.filter(Student.bed_assignment == bed)
    if hostel_id:
        query = query.filter(Student.hostel_id == hostel_id)
    if status:
        query = query.filter(Student.status == status)
    if checkin_from:
        query = query.filter(Student.check_in_date >= checkin_from)
    if checkin_to:
        query = query.filter(Student.check_in_date <= checkin_to)
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
   
    # Tenant filtering (if user_hostel_ids provided)
    if user_hostel_ids:
        query = query.filter(Student.hostel_id.in_(user_hostel_ids))
   
    # Sort
    if sort_by:
        sort_col = getattr(Student, sort_by, Student.student_id)
        if sort_order and sort_order.lower() == "desc":
            query = query.order_by(sort_col.desc())
        else:
            query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(Student.student_id)
 
    return query.offset(skip).limit(limit).all()
 
 
def get_student(db: Session, student_id: str) -> Optional[Student]:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if student and hasattr(student, 'hostel_id') and isinstance(student.hostel_id, str):
        try:
            student.hostel_id = int(student.hostel_id)
        except Exception:
            student.hostel_id = None
    return student
 
 
def create_student(db: Session, student_in: StudentCreate) -> Student:
    data = student_in.dict()
    # extract password fields if present
    password = data.pop("password", None)
    data.pop("confirm_password", None)
    # If student already exists, return it (idempotent create)
    existing = db.query(Student).filter(
        (Student.student_id == student_in.student_id) | (Student.student_email == student_in.student_email)
    ).first()
    if existing:
        return existing
 
    # Try to find an existing user by email or phone; if found, reuse and ensure role
    from app.models.user import User as UserModel
 
    existing_user = None
    if student_in.student_email:
        existing_user = db.query(UserModel).filter(UserModel.email == student_in.student_email).first()
    if not existing_user and student_in.student_phone:
        existing_user = db.query(UserModel).filter(UserModel.phone_number == student_in.student_phone).first()
 
    user_repo = UserRepository(db)
    if existing_user:
        # Ensure role is student
        if existing_user.role != UserRole.STUDENT.value:
            existing_user.role = UserRole.STUDENT.value
            db.add(existing_user)
            db.commit()
            db.refresh(existing_user)
        # Activate and verify existing user created by admin/student import
        existing_user.is_active = True
        if getattr(existing_user, "email", None):
            existing_user.is_email_verified = True
        if getattr(existing_user, "phone_number", None):
            existing_user.is_phone_verified = True
        existing_user.is_verified = True
        db.add(existing_user)
        db.commit()
        db.refresh(existing_user)
        user = existing_user
    else:
        # Build a username and ensure it's unique to avoid DB unique constraint failures
        base_username = (student_in.student_email.split("@")[0] if student_in.student_email else student_in.student_id)
        username = base_username
        suffix = 0
        from app.models.user import User as UserModel
        while db.query(UserModel).filter(UserModel.username == username).first():
            suffix += 1
            username = f"{base_username}{suffix}"
 
        user_payload = SchemaUserCreate(
            email=student_in.student_email,
            phone_number=student_in.student_phone,
            country_code=None,
            username=username,
            full_name=student_in.student_name,
            role=UserRole.STUDENT.value,
            hostel_id=student_in.hostel_id,
            password=password,
        )
 
        try:
            user = user_repo.create(user_payload)
        except Exception as e:
            # Surface a clearer message for upstream handling
            raise ValueError(f"Failed to create linked user: {e}")
 
        # Newly created user: ensure active and verified so student can login immediately
        user.is_active = True
        if getattr(user, "email", None):
            user.is_email_verified = True
        if getattr(user, "phone_number", None):
            user.is_phone_verified = True
        user.is_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)
 
    obj = Student(**data, user_id=user.id)
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
    # Remove dependent records to avoid FK constraint problems.
    # child tables referencing students.student_id include:
    # - student_payments
    # - student_attendance
    # - student_documents
    # - student_status_history
    # Complaints keep denormalized student fields; safely NULL the student_id so complaints remain.
    db.execute(text("DELETE FROM student_payments WHERE student_id = :sid"), {"sid": student_id})
    db.execute(text("DELETE FROM student_attendance WHERE student_id = :sid"), {"sid": student_id})
    db.execute(text("DELETE FROM student_documents WHERE student_id = :sid"), {"sid": student_id})
    db.execute(text("DELETE FROM student_status_history WHERE student_id = :sid"), {"sid": student_id})
    # Make complaints reference explicit - set student_id to NULL to preserve complaint rows and attachments
    db.execute(text("UPDATE complaints SET student_id = NULL WHERE student_id = :sid"), {"sid": student_id})
 
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
 
    # If new_bed is provided try to look up the bed (support id or room/bed numbers)
    bed_obj = None
    if new_bed is not None:
        # if numeric id passed
        try:
            nbid = int(new_bed)
            bed_obj = db.query(Bed).filter(Bed.id == nbid).first()
        except Exception:
            # attempt to locate by room number + bed number when new_room provided
            if new_room:
                bed_obj = find_bed_by_room_and_bed_number(db, new_room, new_bed)
 
    # If bed_obj provided, perform a proper bed transfer and status updates
    if bed_obj:
        # free old bed if present
        if obj.bed_id:
            old_bed_obj = db.query(Bed).filter(Bed.id == obj.bed_id).first()
            if old_bed_obj:
                old_bed_obj.bed_status = BedStatus.AVAILABLE
                db.add(old_bed_obj)
 
        # occupy new bed
        bed_obj.bed_status = BedStatus.OCCUPIED
        db.add(bed_obj)
 
        # update student fk references and legacy text fields
        obj.bed_id = bed_obj.id
        obj.room_id = bed_obj.room_id
        obj.room_assignment = bed_obj.room_number
        obj.bed_assignment = bed_obj.bed_number
 
    else:
        # fallback: update textual room/bed assignments only
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
 
 
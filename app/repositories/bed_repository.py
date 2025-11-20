from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import exc as sa_exc

from app.models.beds import Bed, BedStatus
from app.models.students import Student
from app.schemas.beds import BedCreate, BedUpdate


def create_bed(db: Session, bed_in: BedCreate) -> Bed:
    obj = Bed(**bed_in.dict())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except sa_exc.ProgrammingError as e:
        db.rollback()
        raise RuntimeError("Database schema not initialized: " + str(e))
    except sa_exc.IntegrityError as e:
        db.rollback()
        raise ValueError("Integrity error: " + str(e))
    except Exception:
        db.rollback()
        raise


def get_bed(db: Session, bed_id: int) -> Optional[Bed]:
    return db.query(Bed).filter(Bed.id == bed_id).first()


def list_beds(db: Session, skip: int = 0, limit: int = 100) -> List[Bed]:
    return db.query(Bed).offset(skip).limit(limit).all()


def list_available_beds(db: Session, room_number: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Bed]:
    query = db.query(Bed).filter(Bed.bed_status == BedStatus.AVAILABLE)
    if room_number:
        query = query.filter(Bed.room_number == room_number)
    return query.order_by(Bed.room_number, Bed.bed_number).offset(skip).limit(limit).all()


def find_bed_by_room_and_bed_number(db: Session, room_number: str, bed_number: str) -> Optional[Bed]:
    return db.query(Bed).filter(
        Bed.room_number == room_number,
        Bed.bed_number == bed_number
    ).first()


def update_bed(db: Session, bed: Bed, bed_in: BedUpdate) -> Bed:
    for field, value in bed_in.dict(exclude_unset=True).items():
        setattr(bed, field, value)
    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed


def delete_bed(db: Session, bed: Bed) -> None:
    db.delete(bed)
    db.commit()


def assign_bed_to_student(db: Session, bed: Bed, student_id: str) -> Bed:
    bed.bed_status = BedStatus.OCCUPIED
    db.add(bed)

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    student.room_assignment = bed.room_number
    student.bed_assignment = bed.bed_number
    db.add(student)

    db.commit()
    db.refresh(bed)
    return bed


def release_bed(db: Session, bed: Bed) -> Bed:
    bed.bed_status = BedStatus.AVAILABLE
    db.add(bed)

    db.query(Student).filter(
        Student.room_assignment == bed.room_number,
        Student.bed_assignment == bed.bed_number
    ).update({
        Student.room_assignment: None,
        Student.bed_assignment: None
    })

    db.commit()
    db.refresh(bed)
    return bed


def transfer_student_to_bed(db: Session, student_id: str, new_bed: Bed) -> Bed:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    if student.room_assignment and student.bed_assignment:
        old_bed = find_bed_by_room_and_bed_number(db, student.room_assignment, student.bed_assignment)
        if old_bed:
            old_bed.bed_status = BedStatus.AVAILABLE
            db.add(old_bed)

    new_bed.bed_status = BedStatus.OCCUPIED
    db.add(new_bed)

    student.room_assignment = new_bed.room_number
    student.bed_assignment = new_bed.bed_number
    db.add(student)

    db.commit()
    db.refresh(new_bed)
    return new_bed

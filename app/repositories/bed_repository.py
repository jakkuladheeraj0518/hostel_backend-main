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
    """
    Assign the given bed to the student by id.
    This updates bed.bed_status and sets Student.bed_id/room_id (and keeps legacy text fields in sync).
    All within a single commit.
    """
    # mark the bed occupied
    bed.bed_status = BedStatus.OCCUPIED
    db.add(bed)

    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    # set FK references and keep legacy textual fields in sync
    student.bed_id = bed.id
    student.room_id = bed.room_id
    student.room_assignment = bed.room_number
    student.bed_assignment = bed.bed_number
    db.add(student)

    db.commit()
    db.refresh(bed)
    return bed


def release_bed(db: Session, bed: Bed) -> Bed:
    # make the bed available
    bed.bed_status = BedStatus.AVAILABLE
    db.add(bed)

    # clear assigned student FK/legacy fields where the student references this bed
    db.query(Student).filter(Student.bed_id == bed.id).update({
        Student.bed_id: None,
        Student.room_id: None,
        Student.room_assignment: None,
        Student.bed_assignment: None,
    })

    db.commit()
    db.refresh(bed)
    return bed


def transfer_student_to_bed(db: Session, student_id: str, new_bed: Bed) -> Bed:
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise ValueError("Student not found")
    # if student currently assigned to a bed, free it
    if student.bed_id:
        old_bed = db.query(Bed).filter(Bed.id == student.bed_id).first()
        if old_bed:
            old_bed.bed_status = BedStatus.AVAILABLE
            db.add(old_bed)

    # occupy new bed
    new_bed.bed_status = BedStatus.OCCUPIED
    db.add(new_bed)

    # update student record to reference new bed/room
    student.bed_id = new_bed.id
    student.room_id = new_bed.room_id
    student.room_assignment = new_bed.room_number
    student.bed_assignment = new_bed.bed_number
    db.add(student)

    db.commit()
    db.refresh(new_bed)
    return new_bed

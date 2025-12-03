from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.bed_repository import (
    create_bed as repo_create_bed,
    get_bed as repo_get_bed,
    list_beds as repo_list_beds,
    list_available_beds as repo_list_available_beds,
    update_bed as repo_update_bed,
    delete_bed as repo_delete_bed,
    assign_bed_to_student as repo_assign_bed_to_student,
    release_bed as repo_release_bed,
    transfer_student_to_bed as repo_transfer_student_to_bed,
    find_bed_by_room_and_bed_number as repo_find_bed_by_room_and_bed_number,
)
from app.schemas.beds import BedCreate, BedUpdate
from app.models.beds import Bed


def create_bed(db: Session, bed_in: BedCreate) -> Bed:
    return repo_create_bed(db, bed_in)


def get_bed(db: Session, bed_id: int) -> Optional[Bed]:
    return repo_get_bed(db, bed_id)


def list_beds(db: Session, skip: int = 0, limit: int = 100) -> List[Bed]:
    return repo_list_beds(db, skip=skip, limit=limit)


def list_available_beds(db: Session, room_number: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Bed]:
    return repo_list_available_beds(db, room_number=room_number, skip=skip, limit=limit)


def update_bed(db: Session, bed_id, bed_in: BedUpdate) -> Optional[Bed]:
    bed = repo_get_bed(db, bed_id)
    if not bed:
        return None
    return repo_update_bed(db, bed, bed_in)


def delete_bed(db: Session, bed_id) -> bool:
    bed = repo_get_bed(db, bed_id)
    if not bed:
        return False
    repo_delete_bed(db, bed)
    return True


def assign_bed(db: Session, bed_id: int, student_id: str) -> Optional[Bed]:
    bed = repo_get_bed(db, bed_id)
    if not bed:
        return None
    return repo_assign_bed_to_student(db, bed, student_id)


def release_bed(db: Session, bed_id: int) -> Optional[Bed]:
    bed = repo_get_bed(db, bed_id)
    if not bed:
        return None
    return repo_release_bed(db, bed)


def transfer_student_bed(db: Session, student_id: str, new_bed_id: int) -> Optional[Bed]:
    new_bed = repo_get_bed(db, new_bed_id)
    if not new_bed:
        return None
    return repo_transfer_student_to_bed(db, student_id, new_bed)


def find_bed_by_room_bed(db: Session, room_number: str, bed_number: str) -> Optional[Bed]:
    return repo_find_bed_by_room_and_bed_number(db, room_number, bed_number)


def bulk_assign_beds(db: Session, assignments: List[dict]) -> dict:
    """Bulk assign students to beds.

    assignments: list of dicts with keys `student_id`, `room_number`, `bed_number`.
    Returns a summary dict with counts and error details.
    """
    summary = {"assigned": 0, "errors": []}

    for idx, a in enumerate(assignments, start=1):
        student_id = a.get("student_id")
        room_number = a.get("room_number")
        bed_number = a.get("bed_number")

        if not student_id or not room_number or not bed_number:
            summary["errors"].append({
                "row": idx,
                "error": "missing_field",
                "detail": "student_id, room_number and bed_number are required",
                "input": a,
            })
            continue

        bed = repo_find_bed_by_room_and_bed_number(db, room_number, bed_number)
        if not bed:
            summary["errors"].append({
                "row": idx,
                "error": "bed_not_found",
                "detail": f"Bed not found for room={room_number} bed={bed_number}",
                "input": a,
            })
            continue

        try:
            repo_assign_bed_to_student(db, bed, student_id)
            summary["assigned"] += 1
        except Exception as e:
            summary["errors"].append({
                "row": idx,
                "error": "assignment_failed",
                "detail": str(e),
                "input": a,
            })

    return summary

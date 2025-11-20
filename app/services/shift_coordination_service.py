from sqlalchemy.orm import Session
import app.repositories.shift_coordination_repositories as repo

from app.schemas.shift_coordination_schemas import (
    ShiftCreate, ShiftScheduleCreate, TaskCreate, TaskUpdate,
    TaskDelegationCreate, HandoverCreate, HandoverItemCreate, CoordinationMeetingCreate
)


# ================== SHIFT ===================
def create_shift_service(db: Session, shift_data: ShiftCreate):
    return repo.create_shift(db, shift_data)


def get_shifts_service(db: Session):
    return repo.get_all_shifts(db)


# ================== SCHEDULE ===================
def create_shift_schedule_service(db: Session, schedule_data: ShiftScheduleCreate):
    return repo.create_shift_schedule(db, schedule_data)


# ================== TASK ===================
def create_task_service(db: Session, task_data: TaskCreate):
    return repo.create_task(db, task_data)


def update_task_service(db: Session, task_id: int, update_data: TaskUpdate):
    return repo.update_task(db, task_id, update_data)


# ================== DELEGATION ===================
def delegate_task_service(db: Session, delegation_data: TaskDelegationCreate):
    return repo.create_task_delegation(db, delegation_data)


# ================== HANDOVER ===================
def create_handover_service(db: Session, handover_data: HandoverCreate):
    return repo.create_handover(db, handover_data)


def add_handover_item_service(db: Session, item_data: HandoverItemCreate):
    return repo.create_handover_item(db, item_data)


# ================== COORDINATION MEETING ===================
def create_meeting_service(db: Session, meeting_data: CoordinationMeetingCreate):
    return repo.create_coordination_meeting(db, meeting_data)


def get_meetings_by_hostel_service(db: Session, hostel_id: int):
    return repo.get_meetings_by_hostel(db, hostel_id)

from sqlalchemy.orm import Session
from app.models.shift_coordination_models import (
    Shift, ShiftSchedule, Task, TaskDelegation,
    ShiftHandover, HandoverItem, SupervisorCoordination
)


def create_shift(db: Session, shift_data):
    shift = Shift(**shift_data.dict())
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


def get_all_shifts(db: Session):
    return db.query(Shift).all()


def create_shift_schedule(db: Session, schedule_data):
    schedule = ShiftSchedule(**schedule_data.dict())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def create_task(db: Session, task_data):
    task = Task(**task_data.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, update_data):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


def create_task_delegation(db: Session, delegation_data):
    delegation = TaskDelegation(**delegation_data.dict())
    db.add(delegation)
    db.commit()
    db.refresh(delegation)
    return delegation


def create_handover(db: Session, handover_data):
    handover = ShiftHandover(**handover_data.dict())
    db.add(handover)
    db.commit()
    db.refresh(handover)
    return handover


def create_handover_item(db: Session, item_data):
    item = HandoverItem(**item_data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def create_coordination_meeting(db: Session, meeting_data):
    meeting = SupervisorCoordination(**meeting_data.dict())
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def get_meetings_by_hostel(db: Session, hostel_id: int):
    return db.query(SupervisorCoordination).filter(SupervisorCoordination.hostel_id == hostel_id).all()

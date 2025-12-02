# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app.core.database import get_db
# from app.schemas.shift_coordination_schemas import (
#     ShiftCreate, ShiftScheduleCreate, TaskCreate, TaskUpdate,
#     TaskDelegationCreate, HandoverCreate, HandoverItemCreate, CoordinationMeetingCreate
# )
# from app.services import shift_coordination_service as service

# router = APIRouter(
#     prefix="/api/shift-coordination",
#     tags=["Shift Coordination System"]
# )


# # ====================== SHIFT =========================
# @router.post("/shifts", status_code=status.HTTP_201_CREATED)
# def create_shift(shift_data: ShiftCreate, db: Session = Depends(get_db)):
#     return service.create_shift_service(db, shift_data)


# @router.get("/shifts", status_code=status.HTTP_200_OK)
# def get_shifts(db: Session = Depends(get_db)):
#     return service.get_shifts_service(db)


# # ====================== SCHEDULE =========================
# @router.post("/schedules", status_code=status.HTTP_201_CREATED)
# def create_shift_schedule(schedule_data: ShiftScheduleCreate, db: Session = Depends(get_db)):
#     return service.create_shift_schedule_service(db, schedule_data)


# # ====================== TASKS =========================
# @router.post("/tasks", status_code=status.HTTP_201_CREATED)
# def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
#     return service.create_task_service(db, task_data)


# @router.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
# def update_task(task_id: int, update_data: TaskUpdate, db: Session = Depends(get_db)):
#     task = service.update_task_service(db, task_id, update_data)
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return task


# # ====================== DELEGATION =========================
# @router.post("/tasks/delegate", status_code=status.HTTP_201_CREATED)
# def delegate_task(delegation_data: TaskDelegationCreate, db: Session = Depends(get_db)):
#     return service.delegate_task_service(db, delegation_data)


# # ====================== HANDOVER =========================
# @router.post("/handovers", status_code=status.HTTP_201_CREATED)
# def create_handover(handover_data: HandoverCreate, db: Session = Depends(get_db)):
#     return service.create_handover_service(db, handover_data)


# @router.post("/handover-items", status_code=status.HTTP_201_CREATED)
# def add_handover_item(item_data: HandoverItemCreate, db: Session = Depends(get_db)):
#     return service.add_handover_item_service(db, item_data)


# # ====================== COORDINATION MEETINGS =========================
# @router.post("/meetings", status_code=status.HTTP_201_CREATED)
# def create_meeting(meeting_data: CoordinationMeetingCreate, db: Session = Depends(get_db)):
#     return service.create_meeting_service(db, meeting_data)


# @router.get("/meetings/{hostel_id}", status_code=status.HTTP_200_OK)
# def get_meetings(hostel_id: int, db: Session = Depends(get_db)):
#     return service.get_meetings_by_hostel_service(db, hostel_id)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.shift_coordination_schemas import (
    ShiftCreate, ShiftScheduleCreate, TaskCreate, TaskUpdate,
    TaskDelegationCreate, HandoverCreate, HandoverItemCreate,
    CoordinationMeetingCreate
)
from app.services import shift_coordination_service as service

# RBAC imports
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required
from app.models.user import User


router = APIRouter(
    prefix="/api/shift-coordination",
    tags=["Shift Coordination System"]
)


# -----------------------------------------------------------
# SHIFT — Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/shifts", status_code=status.HTTP_201_CREATED)
def create_shift(
    shift_data: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_SHIFTS)),
):
    return service.create_shift_service(db, shift_data)


@router.get("/shifts", status_code=status.HTTP_200_OK)
def get_shifts(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_SHIFTS)),
):
    return service.get_shifts_service(db)


# -----------------------------------------------------------
# SCHEDULE — Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/schedules", status_code=status.HTTP_201_CREATED)
def create_shift_schedule(
    schedule_data: ShiftScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN])),
    _: None = Depends(permission_required(Permission.MANAGE_SHIFTS)),
):
    return service.create_shift_schedule_service(db, schedule_data)


# -----------------------------------------------------------
# TASKS — Supervisor + Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_TASKS)),
):
    return service.create_task_service(db, task_data)


@router.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def update_task(
    task_id: int,
    update_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_TASKS)),
):
    task = service.update_task_service(db, task_id, update_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# -----------------------------------------------------------
# DELEGATION — Supervisor + Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/tasks/delegate", status_code=status.HTTP_201_CREATED)
def delegate_task(
    delegation_data: TaskDelegationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_TASKS)),
):
    return service.delegate_task_service(db, delegation_data)


# -----------------------------------------------------------
# HANDOVER — Supervisor + Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/handovers", status_code=status.HTTP_201_CREATED)
def create_handover(
    handover_data: HandoverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_HANDOVER)),
):
    return service.create_handover_service(db, handover_data)


@router.post("/handover-items", status_code=status.HTTP_201_CREATED)
def add_handover_item(
    item_data: HandoverItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_HANDOVER)),
):
    return service.add_handover_item_service(db, item_data)


# -----------------------------------------------------------
# COORDINATION MEETINGS — Supervisor + Admin + SuperAdmin
# -----------------------------------------------------------
@router.post("/meetings", status_code=status.HTTP_201_CREATED)
def create_meeting(
    meeting_data: CoordinationMeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.MANAGE_MEETINGS)),
):
    return service.create_meeting_service(db, meeting_data)


@router.get("/meetings/{hostel_id}", status_code=status.HTTP_200_OK)
def get_meetings(
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required([Role.ADMIN, Role.SUPERADMIN, Role.SUPERVISOR])),
    _: None = Depends(permission_required(Permission.READ_MEETINGS)),
):
    return service.get_meetings_by_hostel_service(db, hostel_id)

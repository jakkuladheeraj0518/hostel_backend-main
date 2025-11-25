from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.supervisor_repository import (
    create_supervisor as repo_create_supervisor,
    get_supervisor as repo_get_supervisor,
    list_supervisors as repo_list_supervisors,
    update_supervisor as repo_update_supervisor,
    delete_supervisor as repo_delete_supervisor,
    assign_hostel as repo_assign_hostel,
    list_hostels as repo_list_hostels,
    list_activity as repo_list_activity,
    create_admin_override as repo_create_admin_override,
    admin_override_assign_supervisor_hostel as repo_admin_override_assign_supervisor_hostel,
)
from app.schemas.supervisors import SupervisorCreate, SupervisorUpdate
from app.models.supervisors import Supervisor, AdminOverride


def create_supervisor(db: Session, sup_in: SupervisorCreate) -> Supervisor:
    return repo_create_supervisor(db, sup_in)


def get_supervisor(db: Session, employee_id: str) -> Optional[Supervisor]:
    return repo_get_supervisor(db, employee_id)


def list_supervisors(db: Session, skip: int = 0, limit: int = 100, name: Optional[str] = None, role: Optional[str] = None, department: Optional[str] = None) -> List[Supervisor]:
    return repo_list_supervisors(db, skip=skip, limit=limit, name=name, role=role, department=department)


def update_supervisor(db: Session, employee_id: str, sup_in: SupervisorUpdate) -> Optional[Supervisor]:
    return repo_update_supervisor(db, employee_id, sup_in)


def delete_supervisor(db: Session, employee_id: str) -> bool:
    return repo_delete_supervisor(db, employee_id)


def assign_supervisor_hostel(db: Session, employee_id: str, hostel_id: int) -> None:
    return repo_assign_hostel(db, employee_id, hostel_id)


def list_supervisor_hostels(db: Session, employee_id: str) -> List[dict]:
    return repo_list_hostels(db, employee_id)


def list_supervisor_activity(db: Session, employee_id: str) -> List[dict]:
    return repo_list_activity(db, employee_id)


# Admin overrides
def create_admin_override(db: Session, admin_employee_id: str, target_supervisor_id: Optional[str], action: str, details: Optional[str]) -> AdminOverride:
    return repo_create_admin_override(db, admin_employee_id, target_supervisor_id, action, details)


def override_assign_supervisor_hostel(db: Session, admin_employee_id: str, target_supervisor_id: str, new_hostel_id: int) -> None:
    return repo_admin_override_assign_supervisor_hostel(db, admin_employee_id, target_supervisor_id, new_hostel_id)

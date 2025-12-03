from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.supervisors import Supervisor, AdminOverride
from app.schemas.supervisors import SupervisorCreate, SupervisorUpdate
from app.core.security import get_password_hash
from app.repositories.auth_repository import create_user as repo_create_user
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate as SchemaUserCreate
from app.core.roles import Role as UserRole


def create_supervisor(db: Session, sup_in: SupervisorCreate) -> Supervisor:
    # Create linked User account for supervisor with hashed password
    data = sup_in.dict()
    password = data.pop("password", None)
    # remove confirm_password as well
    data.pop("confirm_password", None)

    # Use UserRepository to create user with proper role and username
    user_repo = UserRepository(db)
    user_payload = SchemaUserCreate(
        email=sup_in.supervisor_email,
        phone_number=sup_in.supervisor_phone,
        country_code=None,
        username=(sup_in.supervisor_email.split('@')[0] if sup_in.supervisor_email else sup_in.employee_id),
        full_name=sup_in.supervisor_name,
        role=UserRole.SUPERVISOR.value,
        hostel_id=None,
        password=password,
    )

    user = user_repo.create(user_payload)

    # Build Supervisor record from remaining fields and attach user_id
    obj = Supervisor(**data, user_id=user.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _log(db, obj.employee_id, "create", f"created supervisor {obj.employee_id}")
    return obj


def get_supervisor(db: Session, employee_id: str) -> Optional[Supervisor]:
    return db.query(Supervisor).filter(
        Supervisor.employee_id == employee_id
    ).first()


def list_supervisors(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    role: Optional[str] = None,
    department: Optional[str] = None
) -> List[Supervisor]:

    query = db.query(Supervisor)

    if name:
        query = query.filter(Supervisor.supervisor_name.ilike(f"%{name}%"))
    if role:
        query = query.filter(Supervisor.role == role)
    if department:
        query = query.filter(Supervisor.department == department)

    return query.order_by(Supervisor.employee_id).offset(skip).limit(limit).all()


def update_supervisor(db: Session, employee_id: str, sup_in: SupervisorUpdate) -> Optional[Supervisor]:
    obj = get_supervisor(db, employee_id)
    if not obj:
        return None
    
    for field, value in sup_in.dict(exclude_unset=True).items():
        setattr(obj, field, value)

    db.add(obj)
    db.commit()
    db.refresh(obj)

    _log(db, employee_id, "update", "updated supervisor")
    return obj


def delete_supervisor(db: Session, employee_id: str) -> bool:
    obj = get_supervisor(db, employee_id)
    if not obj:
        return False
    # Remove related rows first to avoid FK constraint problems
    # supervisor_activity and supervisor_hostels reference supervisors.employee_id
    # Deleting the parent while children exist caused SQLAlchemy to try and set
    # the FK to NULL which violates the NOT NULL constraint. Delete children
    # explicitly before removing the supervisor.
    db.execute(text("DELETE FROM supervisor_activity WHERE employee_id = :eid"), {"eid": employee_id})
    db.execute(text("DELETE FROM supervisor_hostels WHERE employee_id = :eid"), {"eid": employee_id})
    # Also remove any admin override entries that reference this supervisor (either as admin or target)
    db.execute(text("DELETE FROM admin_overrides WHERE admin_employee_id = :eid OR target_supervisor_id = :eid"), {"eid": employee_id})

    db.delete(obj)
    db.commit()
    return True


def assign_hostel(db: Session, employee_id: str, hostel_id: int) -> None:
    # accept numeric hostel_id and insert as FK-safe value
    db.execute(
        text("INSERT INTO supervisor_hostels (employee_id, hostel_id) VALUES (:eid, :hid)"),
        {"eid": employee_id, "hid": int(hostel_id)}
    )
    db.commit()

    _log(db, employee_id, "assign_hostel", f"assigned to hostel {hostel_id}")


def list_hostels(db: Session, employee_id: str) -> List[dict]:
    rows = db.execute(
        text("SELECT id, hostel_id FROM supervisor_hostels WHERE employee_id = :eid"),
        {"eid": employee_id}
    )
    return [dict(r._mapping) for r in rows]


# ------- Logging -------

def _log(db: Session, employee_id: str, action: str, details: str) -> None:
    db.execute(
        text("""
            INSERT INTO supervisor_activity (employee_id, action, details)
            VALUES (:eid, :action, :details)
        """),
        {"eid": employee_id, "action": action, "details": details}
    )
    db.commit()


def list_activity(db: Session, employee_id: str) -> List[dict]:
    rows = db.execute(
        text("""
            SELECT id, action, details, created_at
            FROM supervisor_activity
            WHERE employee_id = :eid
            ORDER BY created_at DESC
        """),
        {"eid": employee_id}
    )
    return [dict(r._mapping) for r in rows]


# ------- Admin Overrides -------

def create_admin_override(db: Session, admin_employee_id: str, target_supervisor_id: Optional[str],
                          action: str, details: Optional[str]) -> AdminOverride:

    # Validate that admin_employee_id exists in the supervisors table
    admin_exists = db.execute(
        text("SELECT 1 FROM supervisors WHERE employee_id = :admin_id"),
        {"admin_id": admin_employee_id}
    ).fetchone()

    if not admin_exists:
        raise ValueError(f"Admin employee ID {admin_employee_id} does not exist in the supervisors table.")

    o = AdminOverride(
        admin_employee_id=admin_employee_id,
        target_supervisor_id=target_supervisor_id,
        action=action,
        details=details
    )
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


def admin_override_assign_supervisor_hostel(db: Session, admin_employee_id: str,
                                            target_supervisor_id: str, new_hostel_id: int) -> None:

    create_admin_override(
        db,
        admin_employee_id,
        target_supervisor_id,
        "assign_hostel",
        f"Assigned to {new_hostel_id}"
    )

    db.execute(
        text("INSERT INTO supervisor_hostels (employee_id, hostel_id) VALUES (:eid, :hid)"),
        {"eid": target_supervisor_id, "hid": int(new_hostel_id)}
    )
    db.commit()


def list_admin_overrides(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    admin_employee_id: Optional[str] = None,
    target_supervisor_id: Optional[str] = None
) -> List[AdminOverride]:
    """List admin override records with optional filtering."""
    query = db.query(AdminOverride)

    if admin_employee_id:
        query = query.filter(AdminOverride.admin_employee_id == admin_employee_id)
    if target_supervisor_id:
        query = query.filter(AdminOverride.target_supervisor_id == target_supervisor_id)

    return query.order_by(AdminOverride.created_at.desc()).offset(skip).limit(limit).all()

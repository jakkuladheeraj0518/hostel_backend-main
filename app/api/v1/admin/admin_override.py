from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.supervisors import AdminOverride
from app.models.user import User

# RBAC / permissions
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required

router = APIRouter(prefix="/admin/overrides", tags=["overrides"])


# --------------------------------------------------------------------
# Request schema
# --------------------------------------------------------------------
class OverridePayload(BaseModel):
    action: str
    details: Optional[str] = None
    old_state: Optional[dict] = None
    new_state: Optional[dict] = None
    target_supervisor_id: Optional[str] = None
    # Optional: explicitly provide the supervisor employee_id who is acting as admin.
    # If omitted, the endpoint will try to derive it from the authenticated user.
    admin_employee_id: Optional[str] = None


def _get_admin_employee_id(current_user: User) -> str:
    """Helper to get a stable admin identifier."""
    return getattr(current_user, "employee_id", None)


def _create_override_record(
    db: Session,
    admin_employee_id: str,
    action: str,
    details: str,
    payload: OverridePayload,
):
    override_record = AdminOverride(
        admin_employee_id=admin_employee_id,
        action=action,
        details=details,
        target_supervisor_id=payload.target_supervisor_id,
    )
    db.add(override_record)
    db.commit()
    db.refresh(override_record)
    return override_record


# --------------------------------------------------------------------
# Override complaint resolution
# --------------------------------------------------------------------
@router.post("/complaints/{complaint_id}", status_code=status.HTTP_200_OK)
def override_complaint(
    complaint_id: int,
    payload: OverridePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_OVERRIDES)
    ),
):
    """
    Override complaint resolution status/assignee.
    Records action in admin_overrides audit table.
    """
    try:
        # prefer explicit admin_employee_id in payload (useful when caller is a Superadmin)
        admin_employee_id = payload.admin_employee_id or _get_admin_employee_id(current_user)

        if not admin_employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "admin_employee_id is required when your user record is not a Supervisor. "
                    "Provide the supervisor `employee_id` (e.g. 'EMP004') in the payload."
                ),
            )

        # validate supervisor exists to avoid FK violation
        from app.models.supervisors import Supervisor

        found = db.query(Supervisor).filter(Supervisor.employee_id == admin_employee_id).first()
        if not found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Admin employee_id '{admin_employee_id}' is not registered as a Supervisor. "
                    "Provide a valid supervisor.employee_id (e.g. 'EMP004')."
                ),
            )

        details = payload.details or f"Changed complaint {complaint_id}: {payload.action}"

        override_record = _create_override_record(
            db=db,
            admin_employee_id=admin_employee_id,
            action=f"override_complaint_{complaint_id}",
            details=details,
            payload=payload,
        )

        return {
            "detail": "Complaint override recorded",
            "override_id": override_record.id,
            "action": payload.action,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------
# Override attendance entry
# --------------------------------------------------------------------
@router.post("/attendance/{attendance_id}", status_code=status.HTTP_200_OK)
def override_attendance(
    attendance_id: int,
    payload: OverridePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_OVERRIDES)
    ),
):
    """
    Override attendance entry (mark present/absent, etc.).
    Records action in admin_overrides audit table.
    """
    try:
        admin_employee_id = payload.admin_employee_id or _get_admin_employee_id(current_user)
        if not admin_employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "admin_employee_id is required when your user record is not a Supervisor. "
                    "Provide the supervisor `employee_id` (e.g. 'EMP004') in the payload."
                ),
            )

        from app.models.supervisors import Supervisor
        found = db.query(Supervisor).filter(Supervisor.employee_id == admin_employee_id).first()
        if not found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Admin employee_id '{admin_employee_id}' is not registered as a Supervisor. "
                    "Provide a valid supervisor.employee_id (e.g. 'EMP004')."
                ),
            )

        details = payload.details or f"Changed attendance {attendance_id}: {payload.action}"

        override_record = _create_override_record(
            db=db,
            admin_employee_id=admin_employee_id,
            action=f"override_attendance_{attendance_id}",
            details=details,
            payload=payload,
        )

        return {
            "detail": "Attendance override recorded",
            "override_id": override_record.id,
            "action": payload.action,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------
# Override maintenance approval
# --------------------------------------------------------------------
@router.post("/maintenance/{request_id}", status_code=status.HTTP_200_OK)
def override_maintenance(
    request_id: int,
    payload: OverridePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_OVERRIDES)
    ),
):
    """
    Override maintenance request (approve/reject/cancel).
    Records action in admin_overrides audit table.
    """
    try:
        admin_employee_id = payload.admin_employee_id or _get_admin_employee_id(current_user)
        if not admin_employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "admin_employee_id is required when your user record is not a Supervisor. "
                    "Provide the supervisor `employee_id` (e.g. 'EMP004') in the payload."
                ),
            )

        from app.models.supervisors import Supervisor
        found = db.query(Supervisor).filter(Supervisor.employee_id == admin_employee_id).first()
        if not found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Admin employee_id '{admin_employee_id}' is not registered as a Supervisor. "
                    "Provide a valid supervisor.employee_id (e.g. 'EMP004')."
                ),
            )

        details = payload.details or f"Changed maintenance request {request_id}: {payload.action}"

        override_record = _create_override_record(
            db=db,
            admin_employee_id=admin_employee_id,
            action=f"override_maintenance_{request_id}",
            details=details,
            payload=payload,
        )

        return {
            "detail": "Maintenance override recorded",
            "override_id": override_record.id,
            "action": payload.action,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------
# Reassign supervisor task
# --------------------------------------------------------------------
@router.post("/tasks/{task_id}/reassign", status_code=status.HTTP_200_OK)
def reassign_task(
    task_id: int,
    payload: OverridePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_OVERRIDES)
    ),
):
    """
    Reassign task from one supervisor to another.
    Records action in admin_overrides audit table.
    """
    try:
        admin_employee_id = payload.admin_employee_id or _get_admin_employee_id(current_user)
        if not admin_employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "admin_employee_id is required when your user record is not a Supervisor. "
                    "Provide the supervisor `employee_id` (e.g. 'EMP004') in the payload."
                ),
            )

        from app.models.supervisors import Supervisor
        found = db.query(Supervisor).filter(Supervisor.employee_id == admin_employee_id).first()
        if not found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Admin employee_id '{admin_employee_id}' is not registered as a Supervisor. "
                    "Provide a valid supervisor.employee_id (e.g. 'EMP004')."
                ),
            )

        details = payload.details or f"Reassigned task {task_id} to {payload.target_supervisor_id}"

        override_record = _create_override_record(
            db=db,
            admin_employee_id=admin_employee_id,
            action=f"reassign_task_{task_id}",
            details=details,
            payload=payload,
        )

        return {
            "detail": "Task reassignment recorded",
            "override_id": override_record.id,
            "task_id": task_id,
            "new_assignee": payload.target_supervisor_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------
# Emergency hostel access
# --------------------------------------------------------------------
@router.post("/emergency-access", status_code=status.HTTP_200_OK)
def emergency_access(
    payload: OverridePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(
        permission_required(Permission.MANAGE_OVERRIDES)
    ),
):
    """
    Grant temporary elevated rights / emergency access to a hostel or resource.
    Records action in admin_overrides audit table.
    """
    try:
        admin_employee_id = payload.admin_employee_id or _get_admin_employee_id(current_user)
        if not admin_employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "admin_employee_id is required when your user record is not a Supervisor. "
                    "Provide the supervisor `employee_id` (e.g. 'EMP004') in the payload."
                ),
            )

        from app.models.supervisors import Supervisor
        found = db.query(Supervisor).filter(Supervisor.employee_id == admin_employee_id).first()
        if not found:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Admin employee_id '{admin_employee_id}' is not registered as a Supervisor. "
                    "Provide a valid supervisor.employee_id (e.g. 'EMP004')."
                ),
            )

        details = payload.details or "Emergency access granted to supervisor"

        override_record = _create_override_record(
            db=db,
            admin_employee_id=admin_employee_id,
            action="emergency_access_granted",
            details=details,
            payload=payload,
        )

        return {
            "detail": "Emergency access granted and recorded",
            "override_id": override_record.id,
            "target": payload.target_supervisor_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
import csv
from io import StringIO
 
from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import (
    role_required,
    permission_required,
    get_current_active_user,
    get_repository_context,
    get_user_hostel_ids,
)
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, AdminCreate
from app.repositories.user_repository import UserRepository
from app.services.permission_service import PermissionService
from app.core.security import get_password_hash
 
from app.schemas.students import (
    StudentCreate,
    StudentOut,
    StudentUpdate,
    PaymentOut,
    PaymentCreate,
    AttendanceOut,
    StudentDocumentOut,
    StudentDocumentCreate,
    AttendanceCreate,
)
from app.services.student_service import (
    list_students as service_list_students,
    get_student as service_get_student,
    create_student as service_create_student,
    update_student as service_update_student,
    delete_student as service_delete_student,
    set_student_status as service_set_student_status,
    transfer_student as service_transfer_student,
    get_student_history as service_get_student_history,
    create_payment as service_create_payment,
    list_payments as service_list_payments,
    create_attendance as service_create_attendance,
    list_attendance as service_list_attendance,
    create_student_document as service_create_student_document,
    list_student_documents as service_list_student_documents,
)
 
router = APIRouter(prefix="/api/v1/admin/students", tags=["students"])
 
 
# -------------------------------------------------
# LIST STUDENTS - Admin + Supervisor + Super Admin
# Student Search & Filter APIs
# -------------------------------------------------
@router.get("/", response_model=List[StudentOut])
def read_students(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    room: Optional[str] = None,
    payment_status: Optional[str] = None,
    attendance_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    return service_list_students(
        db,
        skip=skip,
        limit=limit,
        name=name,
        room=room,
        payment_status=payment_status,
        attendance_status=attendance_status,
    )
 
 
# -------------------------------------------------
# GET ONE STUDENT - Admin + Supervisor + Super Admin
# Student Profile Management APIs (read)
# -------------------------------------------------
@router.get("/{student_id}", response_model=StudentOut)
def read_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    student = service_get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
 
 
# -------------------------------------------------
# CREATE STUDENT - Hostel Admin + Super Admin
# Student Profile Management APIs (create)
# -------------------------------------------------
@router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(
    item: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    try:
        return service_create_student(db, item)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "student_email" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with email '{item.student_email}' already exists",
            )
        if "student_id" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Student with id '{item.student_id}' already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this information already exists",
        )
 
 
# -------------------------------------------------
# UPDATE STUDENT - Hostel Admin + Super Admin
# Student Profile Management APIs (update)
# -------------------------------------------------
@router.put("/{student_id}", response_model=StudentOut, operation_id="admin_update_student")
def update_student(
    student_id: str,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    try:
        updated = service_update_student(db, student_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Student not found")
        return updated
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "student_email" in error_msg:
            email = getattr(payload, "student_email", None)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Student with email '{email}' already exists"
                    if email
                    else "A student with this email already exists"
                ),
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this information already exists",
        )
 
 
# -------------------------------------------------
# DELETE STUDENT - Hostel Admin + Super Admin
# Student Profile Management APIs (delete)
# -------------------------------------------------
@router.delete(
    "/{student_id}",
    status_code=status.HTTP_200_OK,
    operation_id="admin_delete_student",
)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    ok = service_delete_student(db, student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Student not found")
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Student deleted"}
    )
 
 
# -------------------------------------------------
# SET STUDENT STATUS - Hostel Admin + Super Admin
# Student Status Management (active/inactive/alumni)
# -------------------------------------------------
@router.post("/{student_id}/status", response_model=StudentOut)
def set_status(
    student_id: str,
    new_status: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    updated = service_set_student_status(db, student_id, new_status, notes)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated
 
 
# -------------------------------------------------
# TRANSFER STUDENT - Hostel Admin + Super Admin
# Student transfer (room/bed/hostel)
# -------------------------------------------------
@router.post("/{student_id}/transfer", response_model=StudentOut)
def transfer(
    student_id: str,
    new_room: Optional[str] = None,
    new_bed: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    updated = service_transfer_student(db, student_id, new_room, new_bed, notes)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")
    return updated
 
 
# -------------------------------------------------
# STUDENT HISTORY - Admin + Supervisor + Super Admin
# Student Status Management (history)
# -------------------------------------------------
@router.get("/{student_id}/history")
def history(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    return service_get_student_history(db, student_id)
 
 
# -------------------------------------------------
# PAYMENTS
# -------------------------------------------------
 
# Create payment - Hostel Admin + Super Admin
@router.post(
    "/{student_id}/payments",
    response_model=PaymentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    student_id: str,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_PAYMENTS)),
):
    return service_create_payment(db, student_id, payload)
 
 
# List payments - Hostel Admin + Super Admin (financial read)
@router.get("/{student_id}/payments", response_model=List[PaymentOut])
def list_payments(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.VIEW_PAYMENTS)),
):
    return service_list_payments(db, student_id)
 
 
# -------------------------------------------------
# ATTENDANCE
# -------------------------------------------------
 
# Create attendance - Admin + Supervisor + Super Admin
@router.post(
    "/{student_id}/attendance",
    response_model=AttendanceOut,
    status_code=status.HTTP_201_CREATED,
)
def create_attendance(
    student_id: str,
    payload: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ATTENDANCE)),
):
    return service_create_attendance(db, student_id, payload)
 
 
# List attendance - Admin + Supervisor + Super Admin
@router.get("/{student_id}/attendance", response_model=List[AttendanceOut])
def list_attendance(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_ATTENDANCE)),
):
    return service_list_attendance(db, student_id)
 
 
# -------------------------------------------------
# DOCUMENTS
# -------------------------------------------------
 
# Create document - Hostel Admin + Super Admin
@router.post(
    "/{student_id}/documents",
    response_model=StudentDocumentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    student_id: str,
    payload: StudentDocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    return service_create_student_document(db, student_id, payload)
 
 
# List documents - Admin + Supervisor + Super Admin
@router.get("/{student_id}/documents", response_model=List[StudentDocumentOut])
def list_documents(
    student_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN, Role.SUPERVISOR])
    ),
    _: None = Depends(permission_required(Permission.READ_HOSTEL)),
):
    return service_list_student_documents(db, student_id)
 
 
# -------------------------------------------------
# BULK IMPORT STUDENTS - Hostel Admin + Super Admin
# Student Search & Filter APIs (bulk import)
# -------------------------------------------------
@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def bulk_import_students(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.MANAGE_STUDENTS)),
):
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(StringIO(content))
 
    alias_map = {
        "id": "student_id",
        "student id": "student_id",
        "student_id": "student_id",
        "name": "student_name",
        "student name": "student_name",
        "student_name": "student_name",
        "email": "student_email",
        "student email": "student_email",
        "student_email": "student_email",
        "phone": "student_phone",
        "mobile": "student_phone",
        "student phone": "student_phone",
        "student_phone": "student_phone",
        "dob": "date_of_birth",
        "date of birth": "date_of_birth",
        "date_of_birth": "date_of_birth",
        "guardian": "guardian_name",
        "guardian_name": "guardian_name",
        "guardian phone": "guardian_phone",
        "guardian_phone": "guardian_phone",
        "emergency": "emergency_contact",
        "emergency_contact": "emergency_contact",
        "checkin": "check_in_date",
        "check_in": "check_in_date",
        "check_in_date": "check_in_date",
        "room": "room_assignment",
        "room_assignment": "room_assignment",
        "bed": "bed_assignment",
        "bed_assignment": "bed_assignment",
        "status": "status",
    }
    required = {"student_id", "student_name", "student_email", "student_phone"}
 
    created = 0
    failed = 0
    errors = []
 
    def norm_key(k: str) -> str:
        return (k or "").strip().lower()
 
    for idx, row in enumerate(reader, start=2):
        normalized = {}
        for k, v in row.items():
            key = alias_map.get(norm_key(k), None)
            if not key:
                continue
            normalized[key] = (v.strip() if isinstance(v, str) else v) or None
 
        missing = [k for k in required if not normalized.get(k)]
        if missing:
            failed += 1
            errors.append({"row": idx, "error": f"missing required: {', '.join(missing)}"})
            continue
 
        for date_key in ("date_of_birth", "check_in_date"):
            if normalized.get(date_key):
                try:
                    normalized[date_key] = datetime.strptime(
                        normalized[date_key], "%Y-%m-%d"
                    ).date()
                except Exception:
                    errors.append(
                        {
                            "row": idx,
                            "error": f"invalid date format for {date_key} (use YYYY-MM-DD)",
                        }
                    )
                    failed += 1
                    normalized = None
                    break
        if normalized is None:
            continue
 
        try:
            service_create_student(db, StudentCreate(**normalized))
            created += 1
        except Exception as e:
            failed += 1
            errors.append({"row": idx, "error": str(e)})
            continue
 
    return {"created": created, "failed": failed, "errors": errors}
 
 
# -------------------------------------------------
# EXPORT STUDENTS - Hostel Admin + Super Admin
# Student Search & Filter APIs (export)
# -------------------------------------------------
@router.get("/export")
def export_students(
    name: Optional[str] = None,
    room: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        role_required([Role.SUPERADMIN, Role.ADMIN])
    ),
    _: None = Depends(permission_required(Permission.EXPORT_REPORTS)),
):
    rows = service_list_students(db, skip=0, limit=100000, name=name, room=room)
    buf = StringIO()
    writer = csv.writer(buf)
    headers = [
        "student_id",
        "student_name",
        "student_email",
        "student_phone",
        "date_of_birth",
        "guardian_name",
        "guardian_phone",
        "emergency_contact",
        "check_in_date",
        "room_assignment",
        "bed_assignment",
        "status",
    ]
    writer.writerow(headers)
    for s in rows:
        writer.writerow([getattr(s, h, None) for h in headers])
    buf.seek(0)
 
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=students.csv"},
    )
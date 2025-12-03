"""
Admin management endpoints (SuperAdmin only)
- Create admin
- List admins
- Get admin
- Update admin
- Delete admin
- Upload profile picture
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from pathlib import Path

from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required, get_current_active_user, get_repository_context, get_repository_context_direct, get_user_hostel_ids
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, AdminCreate
from app.repositories.user_repository import UserRepository
from app.services.permission_service import PermissionService
from app.core.security import get_password_hash
from app.config import settings
from fastapi import Body
 

router = APIRouter()

# Profile picture upload directory
UPLOAD_DIR = Path("uploads/profile_pictures")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image_file(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    if not file.filename:
        return False
    
    ext = Path(file.filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def save_profile_picture(file: UploadFile, user_id: int) -> str:
    """Save profile picture and return URL"""
    # Generate unique filename
    ext = Path(file.filename).suffix.lower()
    filename = f"{user_id}_{uuid.uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit"
            )
        buffer.write(content)
    
    # Return relative URL
    return f"/uploads/profile_pictures/{filename}"


@router.post("/admins", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["admin"])
async def create_admin(
    admin_data: AdminCreate,
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """
    Create new hostel admin (SuperAdmin only)
    
    Creates a new admin user with role 'admin'. 
    Requires password and confirm_password (must match).
    """
    # Ensure role is admin
    if admin_data.role and admin_data.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only creates admin users. Role must be 'admin'."
        )
    
    # Password validation is handled by AdminCreate schema validator
    # confirm_password is validated to match password
    
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )
    
    # Check if email already exists
    if admin_data.email and user_repo.get_by_email(admin_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if user_repo.get_by_username(admin_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Check if phone already exists
    if admin_data.phone_number and user_repo.get_by_phone_number(admin_data.phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    
    # Set role to admin explicitly
    admin_data.role = Role.ADMIN.value

    # Validate hostel if provided
    if getattr(admin_data, 'hostel_id', None):
        from app.repositories.hostel_repository import HostelRepository
        hostel_repo = HostelRepository(db)
        hostel = hostel_repo.get_by_id(admin_data.hostel_id)
        if not hostel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Hostel with id={admin_data.hostel_id} does not exist"
            )
    
    # Convert AdminCreate to UserCreate (exclude confirm_password)
    user_create_data = UserCreate(
        email=admin_data.email,
        phone_number=admin_data.phone_number,
        country_code=admin_data.country_code,
        username=admin_data.username,
        full_name=admin_data.full_name,
        role=admin_data.role,
        hostel_id=admin_data.hostel_id,
        password=admin_data.password  # Only password, not confirm_password
    )
    
    # Create admin
    admin = user_repo.create(user_create_data)
    
    # Set admin as active (admins created by SuperAdmin are active by default)
    admin.is_active = True
    admin.is_email_verified = True  # Trust SuperAdmin-created admins
    db.commit()
    db.refresh(admin)
    
    return admin


@router.get("/admins", response_model=List[UserResponse], tags=["admin"])
async def list_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    hostel_id: Optional[int] = Query(None, description="Filter by hostel ID"),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """
    List all admins (SuperAdmin only)
    
    Returns a list of all admin users. Can optionally filter by hostel_id.
    """
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )
    
    # Get all users and filter by admin role
    all_users = user_repo.get_all(skip=skip, limit=limit * 10)  # Get more to filter
    
    # Filter admins
    admins = [u for u in all_users if u.role == Role.ADMIN.value]
    
    # Filter by hostel_id if provided
    if hostel_id:
        admins = [a for a in admins if a.hostel_id == hostel_id]
    
    # Apply limit after filtering
    admins = admins[:limit]
    
    return admins


@router.get("/admins/{admin_id}", response_model=UserResponse, tags=["admin"])
async def get_admin(
    admin_id: int,
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get admin by ID (SuperAdmin only)
    """
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )
    
    admin = user_repo.get_by_id(admin_id)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    # Verify it's an admin
    if admin.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )
    
    return admin


@router.put("/admins/{admin_id}", response_model=UserResponse, tags=["admin"])
async def update_admin(
    admin_id: int,
    admin_data: UserUpdate,
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """
    Update admin (SuperAdmin only)
    """
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )
    
    # Get existing admin
    existing_admin = user_repo.get_by_id(admin_id)
    if not existing_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    # Verify it's an admin
    if existing_admin.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )
    
    # Prevent role change (admins should stay as admin)
    if admin_data.role and admin_data.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change admin role. Use role management endpoints instead."
        )
    
    # Check email uniqueness if updating
    if admin_data.email and admin_data.email != existing_admin.email:
        if user_repo.get_by_email(admin_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check username uniqueness if updating
    if admin_data.username and admin_data.username != existing_admin.username:
        if user_repo.get_by_username(admin_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Check phone uniqueness if updating
    if admin_data.phone_number and admin_data.phone_number != existing_admin.phone_number:
        if user_repo.get_by_phone_number(admin_data.phone_number):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
    
    # Update admin
    updated_admin = user_repo.update(admin_id, admin_data)
    if not updated_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    return updated_admin


@router.delete("/admins/{admin_id}", status_code=status.HTTP_200_OK, tags=["admin"])
async def delete_admin(
    admin_id: int,
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """
    Delete admin (SuperAdmin only)
    """
    # Prevent self-deletion
    if admin_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )
    
    # Get admin to verify
    admin = user_repo.get_by_id(admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    
    # Verify it's an admin
    if admin.role != Role.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not an admin"
        )
    
    # Delete profile picture if exists
    if hasattr(admin, 'profile_picture_url') and admin.profile_picture_url:
        profile_path = Path(admin.profile_picture_url.lstrip('/'))
        if profile_path.exists():
            profile_path.unlink()
    
    # Soft-delete / deactivate admin instead of hard delete to preserve
    # audit log integrity and avoid FK constraint issues.
    try:
        # Anonymize identifying fields to allow reuse of emails/usernames
        import uuid as _uuid
        admin.is_active = False
        admin.is_email_verified = False
        admin.is_phone_verified = False
        # Clear contact info
        admin.email = None
        admin.phone_number = None
        admin.profile_picture_url = None
        # Set a unique placeholder username to avoid uniqueness conflicts
        admin.username = f"deleted_admin_{admin.id}_{_uuid.uuid4().hex[:8]}"
        # Remove password
        admin.hashed_password = None

        db.commit()
        db.refresh(admin)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to deactivate admin")

    return {"message": "Admin deactivated"}


@router.post("/admins/{admin_id}/profile-picture", response_model=dict, tags=["admin"])
async def upload_profile_picture(
    admin_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Upload profile picture for a user (SuperAdmin only).

    Accepts image files (jpg, jpeg, png, gif, webp) up to 5MB.
    This endpoint now works for admins, supervisors, and students — it updates the
    `profile_picture_url` for the user with the given id.
    """
    # Validate file
    if not validate_image_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )
    
    # Get user (admin/supervisor/student)
    user = user_repo.get_by_id(admin_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Delete old profile picture if exists
    if hasattr(user, 'profile_picture_url') and user.profile_picture_url:
        old_path = Path(user.profile_picture_url.lstrip('/'))
        if old_path.exists():
            old_path.unlink()

    # Save new profile picture
    try:
        profile_url = save_profile_picture(file, admin_id)

        # Update user's profile_picture_url
        user.profile_picture_url = profile_url
        db.commit()
        db.refresh(user)

        return {
            "message": "Profile picture uploaded successfully",
            "profile_picture_url": profile_url,
            "user_id": admin_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload profile picture: {str(e)}"
        )


@router.post("/admins/{admin_id}/assign-hostels", response_model=dict, tags=["admin"])
async def assign_hostels_to_admin(
    admin_id: int,
    hostel_ids: List[int] = Body(..., embed=True, description="List of hostel ids to assign"),
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Assign multiple hostels to an admin (SuperAdmin only). Idempotent."""
    tenant_service = __import__('app.services.tenant_service', fromlist=['TenantService']).TenantService(db)
    return tenant_service.assign_admin_to_hostels(admin_id, hostel_ids, current_user.role)


@router.post("/users/supervisors", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["admin"])
async def create_supervisor(
    supervisor_data: AdminCreate,
    current_user: User = Depends(role_required(Role.SUPERADMIN, Role.ADMIN)),
    _perm: User = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
    db: Session = Depends(get_db)
):
    """Create a supervisor (SuperAdmin or Hostel Admin for their hostels)"""
    # reuse creation flow similar to create_admin but set role to supervisor
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )

    # uniqueness checks
    if supervisor_data.email and user_repo.get_by_email(supervisor_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if user_repo.get_by_username(supervisor_data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if supervisor_data.phone_number and user_repo.get_by_phone_number(supervisor_data.phone_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")

    supervisor_data.role = Role.SUPERVISOR.value

    # If current_user is an ADMIN, ensure they can only create supervisors for hostels they manage
    if current_user.role == Role.ADMIN:
        allowed_hostels = get_user_hostel_ids(current_user.id, current_user.role, db)
        target_hostel = getattr(supervisor_data, 'hostel_id', None)
        if target_hostel and target_hostel not in allowed_hostels:
            raise AccessDeniedException("Admin cannot assign supervisor to a hostel they do not manage")

    user_create_data = UserCreate(
        email=supervisor_data.email,
        phone_number=supervisor_data.phone_number,
        country_code=supervisor_data.country_code,
        username=supervisor_data.username,
        full_name=supervisor_data.full_name,
        role=supervisor_data.role,
        hostel_id=getattr(supervisor_data, 'hostel_id', None),
        password=supervisor_data.password
    )

    user = user_repo.create(user_create_data)
    user.is_active = True
    user.is_email_verified = True
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/students", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["admin"])
async def create_student(
    student_data: AdminCreate,
    current_user: User = Depends(role_required(Role.SUPERADMIN, Role.ADMIN)),
    _perm: User = Depends(permission_required(Permission.CREATE_REGISTRATION)),
    db: Session = Depends(get_db)
):
    """Create a student (SuperAdmin or Hostel Admin for their hostels)"""
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )

    # uniqueness checks
    if student_data.email and user_repo.get_by_email(student_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if user_repo.get_by_username(student_data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    if student_data.phone_number and user_repo.get_by_phone_number(student_data.phone_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")

    student_data.role = Role.STUDENT.value

    # If current_user is ADMIN, ensure student is assigned to their hostel
    if current_user.role == Role.ADMIN:
        allowed_hostels = get_user_hostel_ids(current_user.id, current_user.role, db)
        target_hostel = getattr(student_data, 'hostel_id', None)
        if target_hostel and target_hostel not in allowed_hostels:
            raise AccessDeniedException("Admin cannot create student for a hostel they do not manage")

    user_create_data = UserCreate(
        email=student_data.email,
        phone_number=student_data.phone_number,
        country_code=student_data.country_code,
        username=student_data.username,
        full_name=student_data.full_name,
        role=student_data.role,
        hostel_id=getattr(student_data, 'hostel_id', None),
        password=student_data.password
    )

    user = user_repo.create(user_create_data)
    user.is_active = True
    user.is_email_verified = True
    db.commit()
    db.refresh(user)
    return user



@router.put("/users/supervisors/{supervisor_id}", response_model=UserResponse, tags=["admin"])
async def update_supervisor(
    supervisor_id: int,
    supervisor_data: UserUpdate,
    current_user: User = Depends(role_required(Role.SUPERADMIN, Role.ADMIN)),
    _perm: User = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
    db: Session = Depends(get_db)
):
    """Update supervisor (SuperAdmin or Hostel Admin for their hostels)"""
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )

    existing = user_repo.get_by_id(supervisor_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supervisor not found")

    if existing.role != Role.SUPERVISOR.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a supervisor")

    # Prevent role change
    if supervisor_data.role and supervisor_data.role != Role.SUPERVISOR.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change supervisor role")

    # If ADMIN is updating, ensure the target supervisor belongs to one of their hostels
    if current_user.role == Role.ADMIN:
        allowed_hostels = get_user_hostel_ids(current_user.id, current_user.role, db)
        if existing.hostel_id and existing.hostel_id not in allowed_hostels:
            raise AccessDeniedException("Admin cannot modify a supervisor outside their hostels")

    # Check email uniqueness if updating
    if supervisor_data.email and supervisor_data.email != existing.email:
        if user_repo.get_by_email(supervisor_data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Check username uniqueness if updating
    if supervisor_data.username and supervisor_data.username != existing.username:
        if user_repo.get_by_username(supervisor_data.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Check phone uniqueness if updating
    if supervisor_data.phone_number and supervisor_data.phone_number != existing.phone_number:
        if user_repo.get_by_phone_number(supervisor_data.phone_number):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")

    updated = user_repo.update(supervisor_id, supervisor_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supervisor not found")

    return updated


@router.delete("/users/supervisors/{supervisor_id}", status_code=status.HTTP_200_OK, tags=["admin"])
async def delete_supervisor(
    supervisor_id: int,
    current_user: User = Depends(role_required(Role.SUPERADMIN, Role.ADMIN)),
    _perm: User = Depends(permission_required(Permission.MANAGE_SUPERVISORS)),
    db: Session = Depends(get_db)
):
    """Delete supervisor (SuperAdmin or Hostel Admin for their hostels)"""
    # Prevent self-deletion
    if supervisor_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")

    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )

    supervisor = user_repo.get_by_id(supervisor_id)
    if not supervisor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supervisor not found")

    if supervisor.role != Role.SUPERVISOR.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a supervisor")

    # Delete profile picture if exists
    if hasattr(supervisor, 'profile_picture_url') and supervisor.profile_picture_url:
        profile_path = Path(supervisor.profile_picture_url.lstrip('/'))
        if profile_path.exists():
            profile_path.unlink()

    # If ADMIN deleting, ensure supervisor within allowed hostels
    if current_user.role == Role.ADMIN:
        allowed_hostels = get_user_hostel_ids(current_user.id, current_user.role, db)
        if supervisor.hostel_id and supervisor.hostel_id not in allowed_hostels:
            raise AccessDeniedException("Admin cannot delete a supervisor outside their hostels")

    # Soft-delete (deactivate and anonymize) to preserve FK integrity
    try:
        import uuid as _uuid
        supervisor.is_active = False
        supervisor.is_email_verified = False
        supervisor.is_phone_verified = False
        supervisor.email = None
        supervisor.phone_number = None
        supervisor.profile_picture_url = None
        supervisor.username = f"deleted_supervisor_{supervisor.id}_{_uuid.uuid4().hex[:8]}"
        supervisor.hashed_password = None

        db.commit()
        db.refresh(supervisor)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to deactivate supervisor")

    return {"message": "Supervisor deactivated"}


@router.put("/users/students/{student_id}", response_model=UserResponse, tags=["admin"])
async def update_student(
    student_id: int,
    student_data: UserUpdate,
    current_user: User = Depends(role_required(Role.SUPERADMIN, Role.ADMIN)),
    _perm: User = Depends(permission_required(Permission.UPDATE_USER)),
    db: Session = Depends(get_db)
):
    """Update student (SuperAdmin or Hostel Admin for their hostels)"""
    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )

    existing = user_repo.get_by_id(student_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if existing.role != Role.STUDENT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a student")

    # Prevent role change
    if student_data.role and student_data.role != Role.STUDENT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change student role")

    # If ADMIN is updating, ensure the student belongs to one of their hostels
    if current_user.role == Role.ADMIN:
        allowed_hostels = get_user_hostel_ids(current_user.id, current_user.role, db)
        if existing.hostel_id and existing.hostel_id not in allowed_hostels:
            raise AccessDeniedException("Admin cannot modify a student outside their hostels")

    # Check email uniqueness if updating
    if student_data.email and student_data.email != existing.email:
        if user_repo.get_by_email(student_data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Check username uniqueness if updating
    if student_data.username and student_data.username != existing.username:
        if user_repo.get_by_username(student_data.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Check phone uniqueness if updating
    if student_data.phone_number and student_data.phone_number != existing.phone_number:
        if user_repo.get_by_phone_number(student_data.phone_number):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already registered")

    updated = user_repo.update(student_id, student_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    return updated


@router.delete("/users/students/{student_id}", status_code=status.HTTP_200_OK, tags=["admin"])
async def delete_student(
    student_id: int,
    current_user: User = Depends(role_required(Role.SUPERADMIN)),
    db: Session = Depends(get_db)
):
    """Delete student (SuperAdmin only)"""
    # Prevent self-deletion
    if student_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")

    context = get_repository_context(current_user, None, db)
    user_repo = UserRepository(
        db=db,
        user_role=context["user_role"],
        active_hostel_id=context["active_hostel_id"],
        user_hostel_ids=context["user_hostel_ids"]
    )

    student = user_repo.get_by_id(student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if student.role != Role.STUDENT.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not a student")

    # Delete profile picture if exists
    if hasattr(student, 'profile_picture_url') and student.profile_picture_url:
        profile_path = Path(student.profile_picture_url.lstrip('/'))
        if profile_path.exists():
            profile_path.unlink()

    success = user_repo.delete(student_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    return {"message": "Student deleted"}


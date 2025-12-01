from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.roles import Role
from app.core.permissions import Permission
from app.api.deps import role_required, permission_required, get_current_active_user, get_repository_context, get_user_hostel_ids
from app.core.exceptions import AccessDeniedException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, AdminCreate
from app.repositories.user_repository import UserRepository
from app.services.permission_service import PermissionService
from app.core.security import get_password_hash
from app.schemas.mess_menu import (
    MessMenuCreate, MessMenuUpdate, MessMenuResponse,
    MenuDuplicationRequest, MenuApprovalRequest
)
from app.services.mess_menu_service import MessMenuService
from app.dependencies import get_mess_menu_service

router = APIRouter(prefix="/admin/mess-menu", tags=["Admin - Mess Menu"])


@router.post("/", response_model=MessMenuResponse, status_code=status.HTTP_201_CREATED)
def create_menu(
    menu: MessMenuCreate,
    service: MessMenuService = Depends(get_mess_menu_service),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Create a new mess menu (Admin only)
    - Daily, weekly, or monthly menu planning
    - Special diet accommodation
    - Meal timing configuration per hostel
    """
    return service.create_menu(menu)


@router.get("/{menu_id}", response_model=MessMenuResponse)
def get_menu(
    menu_id: int,
    service: MessMenuService = Depends(get_mess_menu_service),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get specific menu by ID (Admin only)
    """
    return service.get_menu(menu_id)


@router.get("/hostel/{hostel_id}", response_model=List[MessMenuResponse])
def get_hostel_menus(
    hostel_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    menu_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service: MessMenuService = Depends(get_mess_menu_service),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get all menus for a specific hostel with filters (Admin only)
    - Filter by menu type (daily/weekly/monthly)
    - Filter by date range
    """
    return service.get_menus_by_hostel(
        hostel_id, skip, limit, menu_type, start_date, end_date
    )


@router.put("/{menu_id}", response_model=MessMenuResponse)
def update_menu(
    menu_id: int,
    menu_update: MessMenuUpdate,
    service: MessMenuService = Depends(get_mess_menu_service),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Update an existing menu (Admin only)
    - Modify menu items, timing, special diets
    """
    return service.update_menu(menu_id, menu_update)


@router.delete("/{menu_id}", status_code=status.HTTP_200_OK)
def delete_menu(
    menu_id: int,
    service: MessMenuService = Depends(get_mess_menu_service),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Delete a menu (Admin only)
    """
    return service.delete_menu(menu_id)


@router.post("/duplicate", response_model=List[MessMenuResponse])
def duplicate_menu(
    duplication_request: MenuDuplicationRequest,
    service: MessMenuService = Depends(get_mess_menu_service),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Duplicate menu across multiple hostels (Admin only)
    - Operational efficiency by copying menus
    - Optionally change target date
    """
    return service.duplicate_menu(duplication_request)


@router.post("/{menu_id}/approve", response_model=MessMenuResponse)
def approve_menu(
    menu_id: int,
    approval: MenuApprovalRequest,
    service: MessMenuService = Depends(get_mess_menu_service),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Approve a menu proposed by supervisor (Admin only)
    - Approval workflow for collaborative management
    """
    return service.approve_menu(menu_id, approval)


@router.get("/hostel/{hostel_id}/dietary-restrictions", response_model=dict)
def get_dietary_restrictions_report(
    hostel_id: int,
    service: MessMenuService = Depends(get_mess_menu_service),
    current_user: User = Depends(role_required(Role.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get dietary restrictions report for a hostel (Admin only)
    - Summary of students with special dietary needs
    - Allergy distribution
    - Diet type distribution
    """
    return service.get_dietary_restrictions_report(hostel_id)
from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import date
from app.schemas.mess_menu import (
    MessMenuCreate, MessMenuUpdate, MessMenuResponse,
    MenuFeedbackResponse, MealPreferenceResponse
)
from app.services.mess_menu_service import MessMenuService
from app.dependencies import get_mess_menu_service

router = APIRouter(prefix="/supervisor/mess-menu", tags=["Supervisor - Mess Menu"])


@router.post("/", response_model=MessMenuResponse, status_code=status.HTTP_201_CREATED)
def propose_menu(
    menu: MessMenuCreate,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Propose a new menu for admin approval (Supervisor)
    - Daily menu management based on weekly/monthly plans
    - Propose menu modifications
    """
    return service.create_menu(menu)


@router.get("/{menu_id}", response_model=MessMenuResponse)
def get_menu(
    menu_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Get specific menu by ID (Supervisor)
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
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Get all menus for supervised hostel (Supervisor)
    - View and manage daily menus
    """
    return service.get_menus_by_hostel(
        hostel_id, skip, limit, menu_type, start_date, end_date
    )


@router.put("/{menu_id}", response_model=MessMenuResponse)
def update_menu(
    menu_id: int,
    menu_update: MessMenuUpdate,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Update menu for minor modifications (Supervisor)
    - Ingredient substitutions within guidelines
    - Last-minute dietary emergency accommodations
    - Special occasion updates (with pre-approval)
    """
    return service.update_menu(menu_id, menu_update)


@router.post("/{menu_id}/publish", response_model=MessMenuResponse)
def publish_menu(
    menu_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Publish approved menu for students (Supervisor)
    - Make menu visible to students
    """
    return service.publish_menu(menu_id)


@router.get("/{menu_id}/feedback", response_model=List[MenuFeedbackResponse])
def get_menu_feedback(
    menu_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Get feedback for a specific menu (Supervisor)
    - Quality monitoring
    - Student satisfaction tracking
    """
    return service.get_menu_feedback(menu_id)


@router.get("/{menu_id}/feedback/summary", response_model=dict)
def get_feedback_summary(
    menu_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Get feedback summary with averages (Supervisor)
    - Average ratings for taste, quantity, hygiene
    - Overall satisfaction metrics
    """
    return service.get_feedback_summary(menu_id)


@router.get("/hostel/{hostel_id}/preferences", response_model=List[MealPreferenceResponse])
def get_hostel_preferences(
    hostel_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Get all meal preferences for hostel students (Supervisor)
    - Track special dietary requirements
    - Medical conditions registry
    """
    return service.get_hostel_preferences(hostel_id)


@router.get("/hostel/{hostel_id}/dietary-restrictions", response_model=dict)
def get_dietary_restrictions_report(
    hostel_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Get dietary restrictions report (Supervisor)
    - Summary for meal planning
    - Allergy and medical requirement overview
    """
    return service.get_dietary_restrictions_report(hostel_id)
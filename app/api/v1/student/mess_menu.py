from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import date
from app.schemas.mess_menu import (
    MessMenuResponse,
    MenuFeedbackCreate, MenuFeedbackResponse,
    MealPreferenceCreate, MealPreferenceUpdate, MealPreferenceResponse
)
from app.services.mess_menu_service import MessMenuService
from app.dependencies import get_mess_menu_service

router = APIRouter(prefix="/student/mess-menu", tags=["Student - Mess Menu"])


@router.get("/hostel/{hostel_id}", response_model=List[MessMenuResponse])
def view_hostel_menus(
    hostel_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    View mess menus for daily meal planning (Student)
    - See published menus only
    - Filter by date range
    """
    return service.get_menus_by_hostel(
        hostel_id, skip, limit, menu_type=None, start_date=start_date, end_date=end_date
    )


@router.get("/{menu_id}", response_model=MessMenuResponse)
def view_menu_details(
    menu_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    View specific menu details (Student)
    - Menu items, timing, nutritional info
    """
    return service.get_menu(menu_id)


@router.post("/feedback", response_model=MenuFeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback: MenuFeedbackCreate,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Submit feedback on meal quality (Student)
    - Rate taste, quantity, hygiene
    - Provide comments and suggestions
    """
    return service.create_feedback(feedback)


@router.post("/preferences", response_model=MealPreferenceResponse, status_code=status.HTTP_201_CREATED)
def create_meal_preference(
    preference: MealPreferenceCreate,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Create meal preference profile (Student)
    - Set dietary type (vegetarian, vegan, etc.)
    - Register allergies and medical requirements
    - Specify preferred and disliked items
    """
    return service.create_preference(preference)


@router.get("/preferences/{student_id}/hostel/{hostel_id}", response_model=MealPreferenceResponse)
def get_my_preference(
    student_id: int,
    hostel_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Get student's meal preference (Student)
    """
    return service.get_student_preference(student_id, hostel_id)


@router.put("/preferences/{preference_id}", response_model=MealPreferenceResponse)
def update_meal_preference(
    preference_id: int,
    preference_update: MealPreferenceUpdate,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Update meal preference (Student)
    - Modify dietary requirements
    - Update allergies or preferences
    """
    return service.update_preference(preference_id, preference_update)


@router.get("/hostel/{hostel_id}/today", response_model=List[MessMenuResponse])
def get_today_menu(
    hostel_id: int,
    service: MessMenuService = Depends(get_mess_menu_service)
):
    """
    Get today's published menus (Student)
    - Quick access to today's meals
    """
    today = date.today()
    return service.get_menus_by_hostel(
        hostel_id, 
        skip=0, 
        limit=10, 
        start_date=today, 
        end_date=today
    )
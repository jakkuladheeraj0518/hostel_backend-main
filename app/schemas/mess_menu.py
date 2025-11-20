from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from enum import Enum


class MenuTypeEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class MealTypeEnum(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    SNACKS = "snacks"
    DINNER = "dinner"


class DietTypeEnum(str, Enum):
    REGULAR = "regular"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DIABETIC = "diabetic"
    ALLERGEN_FREE = "allergen_free"


class MenuStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class MenuItem(BaseModel):
    name: str
    description: Optional[str] = None
    diet_types: List[str] = []


class NutritionalInfo(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    fiber: Optional[float] = None


# Menu Schemas
class MessMenuBase(BaseModel):
    hostel_id: int
    menu_type: MenuTypeEnum
    menu_date: date
    meal_type: MealTypeEnum
    items: List[Dict[str, Any]]
    serving_time_start: Optional[time] = None
    serving_time_end: Optional[time] = None
    diet_types: List[str] = []
    nutritional_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    is_special_occasion: bool = False
    occasion_name: Optional[str] = None


class MessMenuCreate(MessMenuBase):
    created_by: int
    created_by_role: str
    status: MenuStatusEnum = MenuStatusEnum.DRAFT


class MessMenuUpdate(BaseModel):
    menu_type: Optional[MenuTypeEnum] = None
    menu_date: Optional[date] = None
    meal_type: Optional[MealTypeEnum] = None
    items: Optional[List[Dict[str, Any]]] = None
    serving_time_start: Optional[time] = None
    serving_time_end: Optional[time] = None
    diet_types: Optional[List[str]] = None
    nutritional_info: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    is_special_occasion: Optional[bool] = None
    occasion_name: Optional[str] = None
    status: Optional[MenuStatusEnum] = None


class MessMenuResponse(MessMenuBase):
    id: int
    status: MenuStatusEnum
    created_by: int
    created_by_role: str
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Feedback Schemas
class MenuFeedbackBase(BaseModel):
    menu_id: int
    rating: int = Field(..., ge=1, le=5)
    taste_rating: Optional[int] = Field(None, ge=1, le=5)
    quantity_rating: Optional[int] = Field(None, ge=1, le=5)
    hygiene_rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = None


class MenuFeedbackCreate(MenuFeedbackBase):
    student_id: int


class MenuFeedbackResponse(MenuFeedbackBase):
    id: int
    student_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Meal Preference Schemas
class MealPreferenceBase(BaseModel):
    hostel_id: int
    diet_type: DietTypeEnum
    allergies: Optional[List[str]] = None
    medical_requirements: Optional[str] = None
    preferred_items: Optional[List[str]] = None
    disliked_items: Optional[List[str]] = None


class MealPreferenceCreate(MealPreferenceBase):
    student_id: int


class MealPreferenceUpdate(BaseModel):
    diet_type: Optional[DietTypeEnum] = None
    allergies: Optional[List[str]] = None
    medical_requirements: Optional[str] = None
    preferred_items: Optional[List[str]] = None
    disliked_items: Optional[List[str]] = None
    is_active: Optional[bool] = None


class MealPreferenceResponse(MealPreferenceBase):
    id: int
    student_id: int
    menu_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Menu Duplication Schema
class MenuDuplicationRequest(BaseModel):
    source_menu_id: int
    target_hostel_ids: List[int]
    target_date: Optional[date] = None
    preserve_timings: bool = True


# Approval Schema
class MenuApprovalRequest(BaseModel):
    approved_by: int
    notes: Optional[str] = None
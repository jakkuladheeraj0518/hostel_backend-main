from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from app.repositories.mess_menu_repository import MessMenuRepository
from app.repositories.hostel_repository import HostelRepository
from app.models.mess_menu import MenuType, MealType
from app.models.user import User
from app.schemas.mess_menu import (
    MessMenuCreate, MessMenuUpdate, MessMenuResponse,
    MenuFeedbackCreate, MenuFeedbackResponse,
    MealPreferenceCreate, MealPreferenceUpdate, MealPreferenceResponse,
    MenuDuplicationRequest, MenuApprovalRequest
)
from fastapi import HTTPException, status


class MessMenuService:
    def __init__(self, db: Session):
        self.repository = MessMenuRepository(db)

    # Menu Management
    def create_menu(self, menu: MessMenuCreate) -> MessMenuResponse:
        # Verify hostel exists
        hostel_repo = HostelRepository(self.repository.db)
        hostel = hostel_repo.get_by_id(menu.hostel_id)
        if not hostel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="hostel id not found"
            )

        # Check if menu already exists for the same date and meal type
        existing_menu = self.repository.get_menu_by_date_and_meal(
            menu.hostel_id,
            menu.menu_date,
            menu.meal_type.value
        )
        
        if existing_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu already exists for {menu.meal_type.value} on {menu.menu_date}"
            )
        
        db_menu = self.repository.create_menu(menu)
        return MessMenuResponse.from_orm(db_menu)

    def get_menu(self, menu_id: int) -> MessMenuResponse:
        db_menu = self.repository.get_menu_by_id(menu_id)
        if not db_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )
        return MessMenuResponse.from_orm(db_menu)

    def get_menus_by_hostel(
        self,
        hostel_id: int,
        skip: int = 0,
        limit: int = 100,
        menu_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MessMenuResponse]:
        # Normalize/validate menu_type param. Accept either MenuType (daily/weekly/monthly)
        # or allow users accidentally passing a MealType (breakfast/lunch/etc.) in the same param.
        menu_type_enum = None
        meal_type_enum = None
        if menu_type:
            try:
                menu_type_enum = MenuType(menu_type)
            except ValueError:
                try:
                    meal_type_enum = MealType(menu_type)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid menu_type value: {menu_type}"
                    )

        db_menus = self.repository.get_menus_by_hostel(
            hostel_id, skip, limit, menu_type=menu_type_enum, start_date=start_date, end_date=end_date, meal_type=meal_type_enum
        )
        return [MessMenuResponse.from_orm(menu) for menu in db_menus]

    def update_menu(self, menu_id: int, menu_update: MessMenuUpdate) -> MessMenuResponse:
        db_menu = self.repository.update_menu(menu_id, menu_update)
        if not db_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )
        return MessMenuResponse.from_orm(db_menu)

    def delete_menu(self, menu_id: int) -> dict:
        success = self.repository.delete_menu(menu_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )
        return {"message": "Menu deleted successfully"}

    def approve_menu(self, menu_id: int, approval: MenuApprovalRequest) -> MessMenuResponse:
        db_menu = self.repository.approve_menu(menu_id, approval.approved_by)
        if not db_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )
        return MessMenuResponse.from_orm(db_menu)

    def publish_menu(self, menu_id: int) -> MessMenuResponse:
        # Check if menu is approved before publishing
        menu = self.repository.get_menu_by_id(menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )
        
        if menu.status.value != "approved":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Menu must be approved before publishing"
            )
        
        db_menu = self.repository.publish_menu(menu_id)
        return MessMenuResponse.from_orm(db_menu)

    def duplicate_menu(self, duplication: MenuDuplicationRequest) -> List[MessMenuResponse]:
        """Duplicate a menu to multiple hostels"""
        source_menu = self.repository.get_menu_by_id(duplication.source_menu_id)
        if not source_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source menu not found"
            )
        
        duplicated_menus = []
        for target_hostel_id in duplication.target_hostel_ids:
            try:
                new_menu = self.repository.duplicate_menu(
                    duplication.source_menu_id,
                    target_hostel_id,
                    duplication.target_date
                )
                if new_menu:
                    duplicated_menus.append(MessMenuResponse.from_orm(new_menu))
            except Exception as e:
                # Log error but continue with other hostels
                print(f"Error duplicating menu to hostel {target_hostel_id}: {str(e)}")
                continue
        
        if not duplicated_menus:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to duplicate menu to any hostel"
            )
        
        return duplicated_menus

    # Feedback Management
    def create_feedback(self, feedback: MenuFeedbackCreate) -> MenuFeedbackResponse:
        # Verify menu exists
        menu = self.repository.get_menu_by_id(feedback.menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )
        # Verify student exists
        student = self.repository.db.query(User).filter(User.id == feedback.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="student id was not found"
            )
        
        db_feedback = self.repository.create_feedback(feedback)
        return MenuFeedbackResponse.from_orm(db_feedback)

    def get_menu_feedback(self, menu_id: int) -> List[MenuFeedbackResponse]:
        feedbacks = self.repository.get_feedback_by_menu(menu_id)
        return [MenuFeedbackResponse.from_orm(feedback) for feedback in feedbacks]

    def get_feedback_summary(self, menu_id: int) -> dict:
        return self.repository.get_feedback_summary(menu_id)

    # Meal Preference Management
    def create_preference(self, preference: MealPreferenceCreate) -> MealPreferenceResponse:
        # Check if student already has an active preference
        # Verify student exists
        student = self.repository.db.query(User).filter(User.id == preference.student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="student id was not found"
            )
        existing = self.repository.get_preference_by_student(
            preference.student_id,
            preference.hostel_id
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student already has an active meal preference. Please update instead."
            )
        
        db_preference = self.repository.create_preference(preference)
        return MealPreferenceResponse.from_orm(db_preference)

    def get_student_preference(self, student_id: int, hostel_id: int) -> MealPreferenceResponse:
        # Verify student exists
        student = self.repository.db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="student id was not found"
            )
        preference = self.repository.get_preference_by_student(student_id, hostel_id)
        if not preference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal preference not found"
            )
        return MealPreferenceResponse.from_orm(preference)

    def get_hostel_preferences(self, hostel_id: int) -> List[MealPreferenceResponse]:
        preferences = self.repository.get_preferences_by_hostel(hostel_id)
        return [MealPreferenceResponse.from_orm(pref) for pref in preferences]

    def update_preference(
        self,
        preference_id: int,
        preference_update: MealPreferenceUpdate
    ) -> MealPreferenceResponse:
        db_preference = self.repository.update_preference(preference_id, preference_update)
        if not db_preference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal preference not found"
            )
        return MealPreferenceResponse.from_orm(db_preference)

    def get_dietary_restrictions_report(self, hostel_id: int) -> dict:
        """Get summary of students with dietary restrictions"""
        restrictions = self.repository.get_students_with_dietary_restrictions(hostel_id)
        
        allergy_summary = {}
        diet_type_summary = {}
        
        for pref in restrictions:
            # Count diet types
            diet_type = pref.diet_type.value
            diet_type_summary[diet_type] = diet_type_summary.get(diet_type, 0) + 1
            
            # Count allergies
            if pref.allergies:
                for allergy in pref.allergies:
                    allergy_summary[allergy] = allergy_summary.get(allergy, 0) + 1
        
        return {
            "total_students_with_restrictions": len(restrictions),
            "diet_type_distribution": diet_type_summary,
            "allergy_distribution": allergy_summary,
            "students_with_medical_requirements": len([p for p in restrictions if p.medical_requirements])
        }
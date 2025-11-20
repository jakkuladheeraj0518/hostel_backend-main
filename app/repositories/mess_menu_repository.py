from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import date, datetime
from app.models.mess_menu import MessMenu, MenuFeedback, MealPreference, MenuStatus, MenuType, MealType
from app.schemas.mess_menu import MessMenuCreate, MessMenuUpdate, MenuFeedbackCreate, MealPreferenceCreate, MealPreferenceUpdate


class MessMenuRepository:
    def __init__(self, db: Session):
        self.db = db

    # CRUD Operations for MessMenu
    def create_menu(self, menu: MessMenuCreate) -> MessMenu:
        db_menu = MessMenu(**menu.dict())
        self.db.add(db_menu)
        self.db.commit()
        self.db.refresh(db_menu)
        return db_menu

    def get_menu_by_id(self, menu_id: int) -> Optional[MessMenu]:
        return self.db.query(MessMenu).filter(MessMenu.id == menu_id).first()

    def get_menus_by_hostel(
        self,
        hostel_id: int,
        skip: int = 0,
        limit: int = 100,
        menu_type: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MessMenu]:
        query = self.db.query(MessMenu).filter(MessMenu.hostel_id == hostel_id)
        
        if menu_type:
            query = query.filter(MessMenu.menu_type == menu_type)
        
        if start_date:
            query = query.filter(MessMenu.menu_date >= start_date)
        
        if end_date:
            query = query.filter(MessMenu.menu_date <= end_date)
        
        return query.order_by(MessMenu.menu_date.desc()).offset(skip).limit(limit).all()

    def get_menu_by_date_and_meal(
        self,
        hostel_id: int,
        menu_date: date,
        meal_type: str
    ) -> Optional[MessMenu]:
        return self.db.query(MessMenu).filter(
            and_(
                MessMenu.hostel_id == hostel_id,
                MessMenu.menu_date == menu_date,
                MessMenu.meal_type == meal_type
            )
        ).first()

    def update_menu(self, menu_id: int, menu_update: MessMenuUpdate) -> Optional[MessMenu]:
        db_menu = self.get_menu_by_id(menu_id)
        if not db_menu:
            return None
        
        update_data = menu_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_menu, field, value)
        
        db_menu.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_menu)
        return db_menu

    def delete_menu(self, menu_id: int) -> bool:
        db_menu = self.get_menu_by_id(menu_id)
        if not db_menu:
            return False
        
        self.db.delete(db_menu)
        self.db.commit()
        return True

    def approve_menu(self, menu_id: int, approved_by: int) -> Optional[MessMenu]:
        db_menu = self.get_menu_by_id(menu_id)
        if not db_menu:
            return None
        
        db_menu.status = MenuStatus.APPROVED
        db_menu.approved_by = approved_by
        db_menu.approved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_menu)
        return db_menu

    def publish_menu(self, menu_id: int) -> Optional[MessMenu]:
        db_menu = self.get_menu_by_id(menu_id)
        if not db_menu:
            return None
        
        db_menu.status = MenuStatus.PUBLISHED
        self.db.commit()
        self.db.refresh(db_menu)
        return db_menu

    def duplicate_menu(
        self,
        source_menu_id: int,
        target_hostel_id: int,
        target_date: Optional[date] = None
    ) -> Optional[MessMenu]:
        source_menu = self.get_menu_by_id(source_menu_id)
        if not source_menu:
            return None
        
        new_menu_data = {
            "hostel_id": target_hostel_id,
            "menu_type": source_menu.menu_type,
            "menu_date": target_date or source_menu.menu_date,
            "meal_type": source_menu.meal_type,
            "items": source_menu.items,
            "serving_time_start": source_menu.serving_time_start,
            "serving_time_end": source_menu.serving_time_end,
            "diet_types": source_menu.diet_types,
            "nutritional_info": source_menu.nutritional_info,
            "notes": source_menu.notes,
            "is_special_occasion": source_menu.is_special_occasion,
            "occasion_name": source_menu.occasion_name,
            "status": MenuStatus.DRAFT,
            "created_by": source_menu.created_by,
            "created_by_role": source_menu.created_by_role
        }
        
        new_menu = MessMenu(**new_menu_data)
        self.db.add(new_menu)
        self.db.commit()
        self.db.refresh(new_menu)
        return new_menu

    # Feedback Operations
    def create_feedback(self, feedback: MenuFeedbackCreate) -> MenuFeedback:
        db_feedback = MenuFeedback(**feedback.dict())
        self.db.add(db_feedback)
        self.db.commit()
        self.db.refresh(db_feedback)
        return db_feedback

    def get_feedback_by_menu(self, menu_id: int) -> List[MenuFeedback]:
        return self.db.query(MenuFeedback).filter(MenuFeedback.menu_id == menu_id).all()

    def get_feedback_summary(self, menu_id: int) -> dict:
        feedbacks = self.get_feedback_by_menu(menu_id)
        
        if not feedbacks:
            return {
                "total_feedbacks": 0,
                "average_rating": 0,
                "average_taste": 0,
                "average_quantity": 0,
                "average_hygiene": 0
            }
        
        return {
            "total_feedbacks": len(feedbacks),
            "average_rating": sum(f.rating for f in feedbacks) / len(feedbacks),
            "average_taste": sum(f.taste_rating for f in feedbacks if f.taste_rating) / len([f for f in feedbacks if f.taste_rating]) if any(f.taste_rating for f in feedbacks) else 0,
            "average_quantity": sum(f.quantity_rating for f in feedbacks if f.quantity_rating) / len([f for f in feedbacks if f.quantity_rating]) if any(f.quantity_rating for f in feedbacks) else 0,
            "average_hygiene": sum(f.hygiene_rating for f in feedbacks if f.hygiene_rating) / len([f for f in feedbacks if f.hygiene_rating]) if any(f.hygiene_rating for f in feedbacks) else 0
        }

    # Meal Preference Operations
    def create_preference(self, preference: MealPreferenceCreate) -> MealPreference:
        db_preference = MealPreference(**preference.dict())
        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)
        return db_preference

    def get_preference_by_student(self, student_id: int, hostel_id: int) -> Optional[MealPreference]:
        return self.db.query(MealPreference).filter(
            and_(
                MealPreference.student_id == student_id,
                MealPreference.hostel_id == hostel_id,
                MealPreference.is_active == True
            )
        ).first()

    def get_preferences_by_hostel(self, hostel_id: int) -> List[MealPreference]:
        return self.db.query(MealPreference).filter(
            and_(
                MealPreference.hostel_id == hostel_id,
                MealPreference.is_active == True
            )
        ).all()

    def update_preference(
        self,
        preference_id: int,
        preference_update: MealPreferenceUpdate
    ) -> Optional[MealPreference]:
        db_preference = self.db.query(MealPreference).filter(
            MealPreference.id == preference_id
        ).first()
        
        if not db_preference:
            return None
        
        update_data = preference_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_preference, field, value)
        
        db_preference.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_preference)
        return db_preference

    def get_students_with_dietary_restrictions(self, hostel_id: int) -> List[MealPreference]:
        return self.db.query(MealPreference).filter(
            and_(
                MealPreference.hostel_id == hostel_id,
                MealPreference.is_active == True,
                or_(
                    MealPreference.allergies.isnot(None),
                    MealPreference.medical_requirements.isnot(None)
                )
            )
        ).all()
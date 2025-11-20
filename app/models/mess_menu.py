from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, ForeignKey, Enum as SQLEnum, Date, Time
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class MenuType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    SNACKS = "snacks"
    DINNER = "dinner"


class DietType(str, enum.Enum):
    REGULAR = "regular"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DIABETIC = "diabetic"
    ALLERGEN_FREE = "allergen_free"


class MenuStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class MessMenu(Base):
    __tablename__ = "mess_menus"

    id = Column(Integer, primary_key=True, index=True)
    hostel_id = Column(Integer, nullable=False, index=True)
    menu_type = Column(SQLEnum(MenuType), nullable=False)
    menu_date = Column(Date, nullable=False, index=True)
    meal_type = Column(SQLEnum(MealType), nullable=False)
    
    # Menu Items (JSON format for flexibility)
    items = Column(JSON, nullable=False)  # [{name, description, diet_types}]
    
    # Timing
    serving_time_start = Column(Time, nullable=True)
    serving_time_end = Column(Time, nullable=True)
    
    # Special Diet Support
    diet_types = Column(JSON, nullable=False, default=list)  # List of supported diet types
    
    # Nutritional Information (optional)
    nutritional_info = Column(JSON, nullable=True)  # {calories, protein, carbs, etc}
    
    # Status and Approval
    status = Column(SQLEnum(MenuStatus), default=MenuStatus.DRAFT)
    created_by = Column(Integer, nullable=False)  # User ID
    created_by_role = Column(String(50), nullable=False)  # admin/supervisor
    approved_by = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    is_special_occasion = Column(Boolean, default=False)
    occasion_name = Column(String(200), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedbacks = relationship("MenuFeedback", back_populates="menu", cascade="all, delete-orphan")
    preferences = relationship("MealPreference", back_populates="menu", cascade="all, delete-orphan")


class MenuFeedback(Base):
    __tablename__ = "menu_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("mess_menus.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, nullable=False, index=True)
    
    rating = Column(Integer, nullable=False)  # 1-5
    taste_rating = Column(Integer, nullable=True)
    quantity_rating = Column(Integer, nullable=True)
    hygiene_rating = Column(Integer, nullable=True)
    
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    menu = relationship("MessMenu", back_populates="feedbacks")


class MealPreference(Base):
    __tablename__ = "meal_preferences"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, nullable=False, index=True)
    hostel_id = Column(Integer, nullable=False, index=True)
    menu_id = Column(Integer, ForeignKey("mess_menus.id", ondelete="CASCADE"), nullable=True)
    
    diet_type = Column(SQLEnum(DietType), nullable=False)
    allergies = Column(JSON, nullable=True)  # List of allergens
    medical_requirements = Column(Text, nullable=True)
    
    preferred_items = Column(JSON, nullable=True)  # List of preferred food items
    disliked_items = Column(JSON, nullable=True)   # List of disliked food items
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    menu = relationship("MessMenu", back_populates="preferences")
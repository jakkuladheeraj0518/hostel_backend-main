from sqlalchemy import Column, String, ForeignKey, Date, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntity
from .enums import MealType


class MessMenu(BaseEntity):
    """Mess Menu model for daily meal planning and management"""
    __tablename__ = "mess_menus"
    
    # Basic information
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    menu_date = Column(Date, nullable=False)
    meal_type = Column(SQLEnum(MealType), nullable=False)  # breakfast, lunch, snacks, dinner
    
    # Menu details
    menu_items = Column(Text, nullable=False)  # JSON string of menu items
    description = Column(Text, nullable=True)
    
    # Nutritional information
    nutritional_info = Column(Text, nullable=True)  # JSON string with calories, protein, etc.
    
    # Special dietary options
    vegetarian_options = Column(Text, nullable=True)
    vegan_options = Column(Text, nullable=True)
    allergen_free_options = Column(Text, nullable=True)
    
    # Workflow
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Integer FK
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Integer FK
    approval_status = Column(String(50), nullable=False, default="pending")  # pending, approved, rejected, published
    
    # Dates
    created_at_time = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Menu planning
    is_weekly_plan = Column(String(1), default='N')  # Y/N
    week_number = Column(String(10), nullable=True)
    
    # Cost and budget
    estimated_cost_per_meal = Column(String(50), nullable=True)
    actual_cost_per_meal = Column(String(50), nullable=True)
    
    # Quality and feedback
    quality_rating = Column(String(10), nullable=True)  # Average rating from students
    feedback_count = Column(String(10), default='0')
    
    # Ingredients
    ingredients = Column(Text, nullable=True)  # JSON string of ingredients
    
    # Vendor/supplier
    supplier_name = Column(String(255), nullable=True)
    supplier_contact = Column(String(20), nullable=True)
    
    # Notes
    supervisor_notes = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    chef_notes = Column(Text, nullable=True)
    
    # Approval workflow
    rejection_reason = Column(Text, nullable=True)
    modification_requested = Column(String(1), default='N')  # Y/N
    modification_notes = Column(Text, nullable=True)
    
    # Special occasions
    is_special_menu = Column(String(1), default='N')  # Y/N
    occasion = Column(String(255), nullable=True)  # festival, birthday, event
    
    # Portion and serving
    portion_size = Column(String(100), nullable=True)
    expected_servings = Column(String(10), nullable=True)
    actual_servings = Column(String(10), nullable=True)
    
    # Wastage tracking
    food_wastage = Column(String(100), nullable=True)
    wastage_notes = Column(Text, nullable=True)
    
    # Relationships
    hostel = relationship("Hostel", foreign_keys=[hostel_id])
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<MessMenu(id={self.id}, date={self.menu_date}, meal={self.meal_type}, status={self.approval_status})>"
    
    @property
    def is_published(self):
        """Check if menu is published"""
        return self.approval_status == "published"
    
    @property
    def requires_approval(self):
        """Check if menu requires admin approval"""
        # Weekly plans and special menus require approval
        return self.is_weekly_plan == 'Y' or self.is_special_menu == 'Y'

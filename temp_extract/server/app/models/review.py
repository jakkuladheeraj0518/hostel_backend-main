from sqlalchemy import Column, String, ForeignKey, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
from .base import BaseEntity
from .enums import ReviewCategory


class Review(BaseEntity):
    """Review model - Updated to match drawio requirements"""
    __tablename__ = "reviews"
    
    # Basic review info (as per drawio)
    student_id = Column(String, nullable=False)  # Changed from user_id as per drawio
    review_rating = Column(Integer, nullable=False)  # Changed field name as per drawio
    review_text = Column(Text, nullable=True)  # Field name as per drawio
    review_category = Column(SQLEnum(ReviewCategory), nullable=False)  # Added from drawio
    
    # Legacy fields for backward compatibility (minimal set)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    overall_rating = Column(Integer, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="reviews")
    hostel = relationship("Hostel", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.overall_rating}, hostel_id={self.hostel_id})>"
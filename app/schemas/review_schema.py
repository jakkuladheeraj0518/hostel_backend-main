from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1-5 stars")
    text: str = Field(..., min_length=10, max_length=1000, description="Review text")
    photo_url: Optional[str] = Field(None, description="Optional photo URL")

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating must be between 1-5 stars")
    text: Optional[str] = Field(None, min_length=10, max_length=1000, description="Review text")
    photo_url: Optional[str] = Field(None, description="Optional photo URL")

class ReviewOut(BaseModel):
    id: int
    hostel_id: int
    student_id: Optional[int]
    rating: int
    text: str
    photo_url: Optional[str]
    is_approved: bool
    helpful_count: int
    is_spam: bool
    created_at: datetime
    updated_at: datetime

class ReviewModerationAction(BaseModel):
    action: str = Field(..., description="approve, reject, or mark_spam")
    reason: Optional[str] = Field(None, description="Reason for moderation action")

class ReviewStats(BaseModel):
    total_reviews: int
    avg_rating: float
    rating_distribution: dict
    recent_reviews: List[ReviewOut]

class ReviewFilter(BaseModel):
    rating: Optional[int] = None
    sort_by: str = Field("newest", description="newest, oldest, highest_rating, lowest_rating, most_helpful")
    is_approved: Optional[bool] = None
    hostel_id: Optional[int] = None

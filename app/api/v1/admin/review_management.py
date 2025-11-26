"""
Enhanced Admin Review Management Routes
Integrated from hemantPawade.zip - provides comprehensive review moderation and analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.review import Review

router = APIRouter(prefix="/admin/review-management", tags=["Admin Review Management"])

@router.get("/reviews")
def get_reviews(
    hostel_id: Optional[int] = None, 
    status: Optional[str] = None, 
    rating: Optional[int] = None, 
    is_spam: Optional[bool] = None,
    skip: int = 0, 
    limit: int = 100, 
    sort_by: str = "newest",
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    """Get all reviews with advanced filtering and sorting"""
    if user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(403, "Forbidden")
    
    query = db.query(Review)
    
    # Apply filters
    if hostel_id:
        query = query.filter(Review.hostel_id == hostel_id)
    if status == "approved":
        query = query.filter(Review.is_approved == True)
    elif status == "pending":
        query = query.filter(Review.is_approved == False)
    if rating:
        query = query.filter(Review.rating == rating)
    if is_spam is not None:
        query = query.filter(Review.is_spam == is_spam)
    
    # Apply sorting
    if sort_by == "newest":
        query = query.order_by(desc(Review.created_at))
    elif sort_by == "oldest":
        query = query.order_by(Review.created_at)
    elif sort_by == "highest_rating":
        query = query.order_by(desc(Review.rating))
    elif sort_by == "lowest_rating":
        query = query.order_by(Review.rating)
    elif sort_by == "most_helpful":
        query = query.order_by(desc(Review.helpful_count))
    
    reviews = query.offset(skip).limit(limit).all()
    return {"reviews": [{"id": r.id, "hostel_id": r.hostel_id, "student_id": r.student_id,
                        "rating": r.rating, "text": r.text, "photo_url": r.photo_url,
                        "is_approved": r.is_approved, "is_spam": r.is_spam,
                        "helpful_count": r.helpful_count, "created_at": r.created_at} for r in reviews]}

@router.get("/reviews/pending")
def get_pending_reviews(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get reviews pending moderation"""
    if user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(403, "Forbidden")
    
    reviews = db.query(Review).filter(
        Review.is_approved == False,
        Review.is_spam == False
    ).order_by(desc(Review.created_at)).offset(skip).limit(limit).all()
    
    return {"reviews": [{"id": r.id, "hostel_id": r.hostel_id, "student_id": r.student_id,
                        "rating": r.rating, "text": r.text, "photo_url": r.photo_url,
                        "created_at": r.created_at} for r in reviews]}

@router.put("/reviews/{review_id}/moderate")
def moderate_review(
    review_id: int, 
    action: str, 
    reason: Optional[str] = None, 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    """Comprehensive review moderation with spam detection"""
    if user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(403, "Forbidden")
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    
    if action == "approve":
        review.is_approved = True
        review.is_spam = False
    elif action == "reject":
        review.is_approved = False
    elif action == "mark_spam":
        review.is_spam = True
        review.is_approved = False
    elif action == "unmark_spam":
        review.is_spam = False
    else:
        raise HTTPException(400, "Invalid action. Use: approve, reject, mark_spam, unmark_spam")
    
    db.commit()
    return {"ok": True, "action": action}

@router.get("/reviews/spam")
def get_spam_reviews(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get reviews marked as spam"""
    if user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(403, "Forbidden")
    
    reviews = db.query(Review).filter(Review.is_spam == True).offset(skip).limit(limit).all()
    return {"reviews": [{"id": r.id, "hostel_id": r.hostel_id, "rating": r.rating, 
                        "text": r.text, "created_at": r.created_at} for r in reviews]}

@router.get("/reviews/analytics")
def get_review_analytics(
    hostel_id: Optional[int] = None, 
    days: int = 30, 
    db: Session = Depends(get_db), 
    user=Depends(get_current_user)
):
    """Get review analytics and insights"""
    if user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(403, "Forbidden")
    
    start_date = datetime.now() - timedelta(days=days)
    
    query = db.query(Review).filter(Review.created_at >= start_date)
    if hostel_id:
        query = query.filter(Review.hostel_id == hostel_id)
    
    total_reviews = query.count()
    approved_reviews = query.filter(Review.is_approved == True).count()
    spam_reviews = query.filter(Review.is_spam == True).count()
    pending_reviews = query.filter(Review.is_approved == False, Review.is_spam == False).count()
    
    avg_rating = query.filter(Review.is_approved == True).with_entities(func.avg(Review.rating)).scalar() or 0
    
    # Rating distribution
    rating_dist = {}
    for i in range(1, 6):
        count = query.filter(Review.rating == i, Review.is_approved == True).count()
        rating_dist[f"{i}_star"] = count
    
    return {
        "period_days": days,
        "total_reviews": total_reviews,
        "approved_reviews": approved_reviews,
        "pending_reviews": pending_reviews,
        "spam_reviews": spam_reviews,
        "avg_rating": round(avg_rating, 2),
        "rating_distribution": rating_dist,
        "approval_rate": round((approved_reviews / total_reviews * 100) if total_reviews > 0 else 0, 2)
    }

@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Delete a review (admin only)"""
    if user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(403, "Forbidden")
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    
    db.delete(review)
    db.commit()
    return {"ok": True}

@router.get("/analytics/dashboard")
def get_admin_dashboard(hostel_id: Optional[int] = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get comprehensive review analytics dashboard"""
    if user.get("role") not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(403, "Forbidden")
    
    # Get basic counts
    query_base = db.query(Review)
    if hostel_id:
        query_base = query_base.filter(Review.hostel_id == hostel_id)
    
    total_reviews = query_base.count()
    approved_reviews = query_base.filter(Review.is_approved == True).count()
    pending_reviews = query_base.filter(Review.is_approved == False, Review.is_spam == False).count()
    spam_reviews = query_base.filter(Review.is_spam == True).count()
    
    # Get average rating
    avg_rating = query_base.filter(Review.is_approved == True).with_entities(func.avg(Review.rating)).scalar()
    
    return {
        "reviews": {
            "total": total_reviews,
            "approved": approved_reviews,
            "pending": pending_reviews,
            "spam": spam_reviews,
            "avg_rating": round(avg_rating, 2) if avg_rating else 0
        }
    }

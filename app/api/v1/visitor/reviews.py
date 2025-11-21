from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from app.core.database import get_db
from app.models.hostel import Hostel
from app.models.review import Review
from app.models.notice import Notice
from app.schemas.review_schema import ReviewCreate



router = APIRouter(prefix="/reviews", tags=["Visitor Reviews"])

@router.post("/reviews/{review_id}/helpful")
def mark_review_helpful(review_id: int, db: Session = Depends(get_db)):
    """Allow visitors to mark reviews as helpful"""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    
    if not review.is_approved or review.is_spam:
        raise HTTPException(400, "Cannot mark this review as helpful")
    
    review.helpful_count += 1
    db.commit()
    return {"ok": True, "helpful_count": review.helpful_count}



@router.get("/reviews/stats")
def get_review_stats(hostel_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get overall review statistics"""
    query = db.query(Review).filter(Review.is_approved == True, Review.is_spam == False)
    
    if hostel_id:
        query = query.filter(Review.hostel_id == hostel_id)
    
    total_reviews = query.count()
    avg_rating = query.with_entities(func.avg(Review.rating)).scalar() or 0
    
    # Rating distribution
    rating_dist = {}
    for i in range(1, 6):
        count = query.filter(Review.rating == i).count()
        rating_dist[f"{i}_star"] = count
    
    return {
        "total_reviews": total_reviews,
        "avg_rating": round(avg_rating, 2),
        "rating_distribution": rating_dist
    }



@router.post("/reviews/{hostel_id}")
def submit_anonymous_review(hostel_id: int, body: ReviewCreate, db: Session = Depends(get_db)):
    # Allow anonymous reviews from visitors
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    if not hostel:
        raise HTTPException(404, "Hostel not found")
    
    review = Review(
        hostel_id=hostel_id, 
        student_id=None,  # Anonymous review
        rating=body.rating, 
        text=body.text, 
        photo_url=body.photo_url,
        is_approved=False  # Requires admin approval
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return {"id": review.id, "message": "Review submitted for approval"}



@router.get("/reviews/trending")
def get_trending_reviews(limit: int = 10, days: int = 7, db: Session = Depends(get_db)):
    """Get trending reviews based on helpful votes and recency"""
    from datetime import datetime, timedelta
    
    start_date = datetime.now() - timedelta(days=days)
    
    reviews = db.query(Review).filter(
        Review.is_approved == True,
        Review.is_spam == False,
        Review.created_at >= start_date,
        Review.helpful_count > 0
    ).order_by(
        desc(Review.helpful_count),
        desc(Review.created_at)
    ).limit(limit).all()
    
    return {"trending_reviews": [
        {
            "id": r.id,
            "hostel_id": r.hostel_id,
            "rating": r.rating,
            "text": r.text[:200] + "..." if len(r.text) > 200 else r.text,
            "helpful_count": r.helpful_count,
            "created_at": r.created_at
        } for r in reviews
    ]}



@router.get("/reviews/summary")
def get_reviews_summary(hostel_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get comprehensive review summary with insights"""
    query = db.query(Review).filter(
        Review.is_approved == True,
        Review.is_spam == False
    )
    
    if hostel_id:
        query = query.filter(Review.hostel_id == hostel_id)
    
    total_reviews = query.count()
    
    if total_reviews == 0:
        return {"message": "No reviews found", "total_reviews": 0}
    
    avg_rating = query.with_entities(func.avg(Review.rating)).scalar()
    
    # Rating distribution
    rating_dist = {}
    for i in range(1, 6):
        count = query.filter(Review.rating == i).count()
        rating_dist[f"{i}_star"] = {
            "count": count,
            "percentage": round((count / total_reviews) * 100, 1)
        }
    
    # Recent trends (last 30 days vs previous 30 days)
    from datetime import datetime, timedelta
    now = datetime.now()
    last_30_days = now - timedelta(days=30)
    previous_30_days = now - timedelta(days=60)
    
    recent_reviews = query.filter(Review.created_at >= last_30_days).count()
    previous_reviews = query.filter(
        Review.created_at >= previous_30_days,
        Review.created_at < last_30_days
    ).count()
    
    trend = "stable"
    if recent_reviews > previous_reviews * 1.2:
        trend = "increasing"
    elif recent_reviews < previous_reviews * 0.8:
        trend = "decreasing"
    
    # Most helpful reviews
    top_reviews = query.filter(Review.helpful_count > 0).order_by(
        desc(Review.helpful_count)
    ).limit(3).all()
    
    return {
        "total_reviews": total_reviews,
        "avg_rating": round(avg_rating, 2),
        "rating_distribution": rating_dist,
        "review_trend": {
            "status": trend,
            "recent_count": recent_reviews,
            "previous_count": previous_reviews
        },
        "top_helpful_reviews": [
            {
                "id": r.id,
                "rating": r.rating,
                "text": r.text[:150] + "..." if len(r.text) > 150 else r.text,
                "helpful_count": r.helpful_count
            } for r in top_reviews
        ]
    }



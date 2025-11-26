"""
Student Review Management Routes
Integrated from hemantPawade.zip - provides review submission and management for students
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.review import Review
from app.schemas.review_schema import ReviewCreate
from app.utils.content_filter import detect_spam, detect_inappropriate_content, content_quality_score

router = APIRouter(prefix="/student/reviews", tags=["Student Reviews"])

@router.post("/{hostel_id}")
def post_review(hostel_id: int, body: ReviewCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Submit a review for a hostel with automatic spam and content filtering"""
    if user.get("role") != "STUDENT":
        raise HTTPException(403, "Only students can post reviews")
    
    # Check if student already reviewed this hostel
    existing = db.query(Review).filter(Review.hostel_id == hostel_id, Review.student_id == user.get("id")).first()
    if existing:
        raise HTTPException(400, "You have already reviewed this hostel")
    
    # Content filtering and spam detection
    is_spam, spam_keywords = detect_spam(body.text)
    is_inappropriate, inappropriate_keywords = detect_inappropriate_content(body.text)
    quality_score = content_quality_score(body.text, body.rating)
    
    if is_inappropriate:
        raise HTTPException(400, f"Review contains inappropriate content: {', '.join(inappropriate_keywords)}")
    
    # Auto-approve high quality reviews, flag low quality ones for manual review
    auto_approve = quality_score > 0.7 and not is_spam
    
    r = Review(
        hostel_id=hostel_id, 
        student_id=user.get("id"), 
        rating=body.rating, 
        text=body.text, 
        photo_url=body.photo_url,
        is_approved=auto_approve
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    
    message = "Review submitted and approved" if auto_approve else "Review submitted for moderation"
    if is_spam:
        message += " (flagged for spam review)"
    
    return {"id": r.id, "message": message, "auto_approved": auto_approve}

@router.get("/my")
def get_my_reviews(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get all reviews submitted by the current student"""
    if user.get("role") != "STUDENT":
        raise HTTPException(403, "Only students can access this")
    
    reviews = db.query(Review).filter(Review.student_id == user.get("id")).all()
    return {"reviews": [{"id": r.id, "hostel_id": r.hostel_id, "rating": r.rating, "text": r.text, 
                        "is_approved": r.is_approved, "helpful_count": r.helpful_count} for r in reviews]}

@router.put("/{review_id}")
def update_review(review_id: int, body: ReviewCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Update an existing review"""
    if user.get("role") != "STUDENT":
        raise HTTPException(403, "Only students can update reviews")
    
    review = db.query(Review).filter(Review.id == review_id, Review.student_id == user.get("id")).first()
    if not review:
        raise HTTPException(404, "Review not found or not owned by you")
    
    review.rating = body.rating
    review.text = body.text
    review.photo_url = body.photo_url
    review.is_approved = False  # Reset approval status
    db.commit()
    return {"ok": True}

@router.post("/{review_id}/helpful")
def mark_review_helpful(review_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Mark a review as helpful"""
    if user.get("role") != "STUDENT":
        raise HTTPException(403, "Only students can mark reviews as helpful")
    
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    
    if not review.is_approved or review.is_spam:
        raise HTTPException(400, "Cannot mark this review as helpful")
    
    # Check if user already marked this review as helpful
    from app.models.review import ReviewHelpful
    existing = db.query(ReviewHelpful).filter(
        ReviewHelpful.review_id == review_id,
        ReviewHelpful.user_id == user.get("id")
    ).first()
    
    if existing:
        raise HTTPException(400, "You have already marked this review as helpful")
    
    # Add helpful vote
    helpful_vote = ReviewHelpful(review_id=review_id, user_id=user.get("id"))
    db.add(helpful_vote)
    
    # Update helpful count
    review.helpful_count += 1
    db.commit()
    return {"ok": True, "helpful_count": review.helpful_count}

@router.delete("/{review_id}")
def delete_my_review(review_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Delete a review"""
    if user.get("role") != "STUDENT":
        raise HTTPException(403, "Only students can delete their reviews")
    
    review = db.query(Review).filter(Review.id == review_id, Review.student_id == user.get("id")).first()
    if not review:
        raise HTTPException(404, "Review not found or not owned by you")
    
    db.delete(review)
    db.commit()
    return {"ok": True}

@router.get("/can-review/{hostel_id}")
def can_review_hostel(hostel_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Check if student can review a specific hostel"""
    if user.get("role") != "STUDENT":
        raise HTTPException(403, "Only students can check review eligibility")
    
    existing = db.query(Review).filter(
        Review.hostel_id == hostel_id, 
        Review.student_id == user.get("id")
    ).first()
    
    return {"can_review": existing is None, "has_existing_review": existing is not None}

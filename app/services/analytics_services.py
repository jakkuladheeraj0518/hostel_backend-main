from sqlalchemy.orm import Session
from app.repositories import analytics_repositories as hostel_summary_repository

def fetch_hostel_summary(db: Session, hostel_id: int):
    return hostel_summary_repository.get_hostel_occupancy_and_revenue(db, hostel_id)

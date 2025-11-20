from sqlalchemy.orm import Session
from sqlalchemy import text

def get_hostel_occupancy_and_revenue(db: Session, hostel_id: int):
    """Call PostgreSQL stored procedure get_hostel_occupancy_and_revenue"""
    query = text("SELECT * FROM get_hostel_occupancy_and_revenue(:hostel_id)")
    result = db.execute(query, {"hostel_id": hostel_id}).fetchall()
    
    # Convert to list of dictionaries for easy JSON serialization
    return [{"occupancy_rate": row[0], "revenue": row[1]} for row in result]

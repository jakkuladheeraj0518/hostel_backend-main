from sqlalchemy import text, func
from sqlalchemy.orm import Session
import json
import logging
from typing import Dict, Any, List
from app.models.hostel import Hostel, Location
from app.models.admin import Admin
from app.models.complaint import Complaint, ComplaintStatus
from app.models.admin_hostel_mapping import AdminHostelMapping

logger = logging.getLogger(__name__)

class DashboardService:
    @staticmethod
    def get_dashboard_and_activities(db: Session) -> Dict[str, Any]:
        try:
            # Get summary statistics using ORM queries on available tables
            total_hostels = db.query(func.count(Hostel.id)).scalar() or 0
            active_admins = db.query(func.count(Admin.id)).filter(Admin.is_active == True).scalar() or 0
            
            # Compute average occupancy from hostels
            avg_occupancy_result = db.query(func.avg(Hostel.current_occupancy)).scalar() or 0.0
            avg_occupancy = round(float(avg_occupancy_result), 2) if avg_occupancy_result else 0.0
            
            # Compute complaint resolution rate as proxy for health
            total_complaints = db.query(func.count(Complaint.id)).scalar() or 0
            resolved_complaints = db.query(func.count(Complaint.id)).filter(
                Complaint.status == ComplaintStatus.RESOLVED
            ).scalar() or 0
            resolution_rate = round(
                (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0.0, 2
            )
            
            dashboard_data = {
                "summary": {
                    "total_hostels": total_hostels,
                    "active_admins": active_admins,
                    "average_occupancy": avg_occupancy,
                    "complaint_resolution_rate": resolution_rate,
                },
                "recent_activities": [],
            }

            # Get top performing hostels by occupancy and total beds
            top_result = db.query(
                Hostel.hostel_name,
                func.coalesce(Location.city, "Unknown").label("city"),
                Hostel.total_beds,
                Hostel.current_occupancy,
                func.round(
                    (Hostel.current_occupancy / func.nullif(Hostel.total_beds, 0) * 100), 2
                ).label("occupancy_rate")
            ).outerjoin(Location, Hostel.location_id == Location.id).order_by(Hostel.current_occupancy.desc()).limit(5).all()

            top_hostels = [
                {
                    "rank": idx + 1,
                    "hostel_name": r[0] or "Unknown",
                    "city": r[1] or "Unknown",
                    "total_beds": r[2] or 0,
                    "current_occupancy": r[3] or 0,
                    "occupancy_rate": float(r[4] or 0.0),
                }
                for idx, r in enumerate(top_result)
            ]

            dashboard_data["top_hostels"] = top_hostels
            return dashboard_data
        except Exception as e:
            logger.exception("Error fetching dashboard")
            raise

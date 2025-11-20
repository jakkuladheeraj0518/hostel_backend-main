from datetime import datetime, timedelta
from typing import Optional, Tuple, List

from app.repositories.complaint_repository import ComplaintRepository
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintUpdate,
    ComplaintAssignment,
    ComplaintResolution,
    ComplaintFeedback,
    ComplaintReopen,
    ComplaintNoteCreate,
    ComplaintFilter,
)
from app.models.complaint import ComplaintStatus


class ComplaintService:
    def __init__(self, repo: ComplaintRepository):
        self.repo = repo

    # -------------------------------------------------------------------------
    # STUDENT ACTIONS
    # -------------------------------------------------------------------------

    async def create_complaint(self, data: ComplaintCreate):
        """Create a new complaint (student)."""
        payload = data.dict()
        payload["status"] = ComplaintStatus.PENDING
        payload["created_at"] = datetime.utcnow()
        payload["sla_deadline"] = datetime.utcnow() + timedelta(days=3)
        return await self.repo.create(payload)

    async def list_complaints(self, filters: ComplaintFilter) -> Tuple[List, int]:
        return await self.repo.list(filters)

    async def get_complaint(self, complaint_id: int):
        return await self.repo.get_by_id(complaint_id)

    async def get_complaint_with_details(self, complaint_id: int):
        return await self.repo.get_with_details(complaint_id)

    async def submit_feedback(self, complaint_id: int, data: ComplaintFeedback):
        updates = {
            "student_feedback": data.student_feedback,
            "student_rating": data.student_rating,
            "status": ComplaintStatus.CLOSED,
            "closed_at": datetime.utcnow()
        }
        return await self.repo.update(complaint_id, updates)

    async def reopen_complaint(self, complaint_id: int, data: ComplaintReopen):
        complaint = await self.repo.get_by_id(complaint_id)
        if not complaint:
            raise ValueError("Complaint not found")

        if complaint.status != ComplaintStatus.CLOSED:
            raise ValueError("Only closed complaints can be reopened")

        updates = {
            "status": ComplaintStatus.REOPENED,
            "is_reopened": True,
            "reopen_reason": data.reopen_reason,
            "updated_at": datetime.utcnow()
        }
        return await self.repo.update(complaint_id, updates)

    async def add_note(self, complaint_id: int, note_data: ComplaintNoteCreate):
        return await self.repo.add_note(
            complaint_id,
            note_data.note,
            note_data.user_name,
            note_data.user_email,
            note_data.is_internal
        )

    async def add_attachment(
        self, complaint_id: int, uploaded_by: str, file_path: str,
        file_name: str, file_type: str, file_size: int
    ):
        return await self.repo.add_attachment(
            complaint_id, uploaded_by, file_path, file_name, file_type, file_size
        )

    # -------------------------------------------------------------------------
    # SUPERVISOR ACTIONS
    # -------------------------------------------------------------------------

    async def update_complaint(self, complaint_id: int, data: ComplaintUpdate):
        """Fix: use dict(exclude_unset=True) to prevent overwriting with None."""
        return await self.repo.update_fields(
            complaint_id,
            data.dict(exclude_unset=True)
        )

    async def assign_complaint(self, complaint_id: int, data: ComplaintAssignment):
        updates = data.dict(exclude_unset=True)
        updates["status"] = ComplaintStatus.IN_PROGRESS
        updates["assigned_at"] = datetime.utcnow()
        return await self.repo.update(complaint_id, updates)

    async def resolve_complaint(self, complaint_id: int, data: ComplaintResolution):
        updates = data.dict(exclude_unset=True)
        updates["status"] = ComplaintStatus.RESOLVED
        updates["resolved_at"] = datetime.utcnow()
        return await self.repo.update(complaint_id, updates)

    async def close_complaint(self, complaint_id: int):
        updates = {
            "status": ComplaintStatus.CLOSED,
            "closed_at": datetime.utcnow()
        }
        return await self.repo.update(complaint_id, updates)

    async def get_supervisor_performance(
        self,
        supervisor_email: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        return await self.repo.get_performance(supervisor_email, start_date, end_date)

    # -------------------------------------------------------------------------
    # ADMIN ACTIONS
    # -------------------------------------------------------------------------

    async def reassign_complaint(self, complaint_id: int, new_name: str, new_email: str):
        updates = {
            "assigned_to_name": new_name,
            "assigned_to_email": new_email,
            "status": ComplaintStatus.IN_PROGRESS,
            "assigned_at": datetime.utcnow()
        }
        return await self.repo.update(complaint_id, updates)

    # -------------------------------------------------------------------------
    # ANALYTICS FIX (must match schema)
    # -------------------------------------------------------------------------

    async def get_analytics(
        self,
        hostel_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        """Fix: Ensure response matches ComplaintAnalytics schema exactly."""
        raw = await self.repo.get_analytics(hostel_name, start_date, end_date)

        return {
            "total_complaints": raw.get("total_complaints", 0),
            "open_complaints": raw.get("open_complaints", 0),
            "resolved_complaints": raw.get("resolved_complaints", 0),
            "average_resolution_time_hours": raw.get("average_resolution_time_hours", 0.0),
            "category_distribution": raw.get("category_distribution", {}),
            "status_distribution": raw.get("status_distribution", {})
        }

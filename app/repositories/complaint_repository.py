from sqlalchemy.future import select
from sqlalchemy import func, and_
from app.models.complaint import Complaint, ComplaintAttachment, ComplaintNote
from typing import Optional, List, Tuple
from datetime import datetime


class ComplaintRepository:
    def __init__(self, db):
        self.db = db

    # -------------------------------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------------------------------
    async def create(self, data: dict) -> Complaint:
        complaint = Complaint(**data)
        self.db.add(complaint)
        self.db.commit()
        self.db.refresh(complaint)
        return complaint

    async def get_by_id(self, complaint_id: int) -> Optional[Complaint]:
        result = self.db.execute(select(Complaint).where(Complaint.id == complaint_id))
        return result.scalar_one_or_none()

    async def get_with_details(self, complaint_id: int):
        """Get complaint along with attachments and notes"""
        result = self.db.execute(select(Complaint).where(Complaint.id == complaint_id))
        complaint = result.scalar_one_or_none()
        if not complaint:
            return None

        attachments_result = self.db.execute(
            select(ComplaintAttachment).where(ComplaintAttachment.complaint_id == complaint_id)
        )
        notes_result = self.db.execute(
            select(ComplaintNote).where(ComplaintNote.complaint_id == complaint_id)
        )

        return {
            "complaint": complaint,
            "attachments": attachments_result.scalars().all(),
            "notes": notes_result.scalars().all(),
        }

    async def update(self, complaint_id: int, updates: dict):
        complaint = await self.get_by_id(complaint_id)
        if not complaint:
            return None
        for key, value in updates.items():
            setattr(complaint, key, value)
        self.db.commit()
        self.db.refresh(complaint)
        return complaint

    async def update_fields(self, complaint_id: int, data):
        updates = data if isinstance(data, dict) else data.dict(exclude_unset=True)
        return await self.update(complaint_id, updates)

    # -------------------------------------------------------------------------
    # FILTERING / LISTING
    # -------------------------------------------------------------------------
    async def list(self, filters) -> Tuple[List[Complaint], int]:
        query = select(Complaint)

        if filters.hostel_name:
            query = query.where(Complaint.hostel_name.ilike(f"%{filters.hostel_name}%"))
        if filters.category:
            query = query.where(Complaint.category == filters.category)
        if filters.status:
            query = query.where(Complaint.status == filters.status)
        if filters.student_email:
            query = query.where(Complaint.student_email == filters.student_email)
        if filters.assigned_to_email:
            query = query.where(Complaint.assigned_to_email == filters.assigned_to_email)

        result_total = self.db.execute(query)
        total_list = result_total.scalars().unique().all()
        total = len(total_list)
        query = query.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)

        result = self.db.execute(query.order_by(Complaint.created_at.desc()))
        return result.scalars().all(), total

    # -------------------------------------------------------------------------
    # ATTACHMENTS & NOTES
    # -------------------------------------------------------------------------
    async def add_attachment(
        self, complaint_id: int, uploaded_by: str,
        file_path: str, file_name: str, file_type: str, file_size: int
    ):
        attachment = ComplaintAttachment(
            complaint_id=complaint_id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            uploaded_by=uploaded_by
        )
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        return attachment

    async def add_note(
        self, complaint_id: int, note: str, user_name: str,
        user_email: str, is_internal: bool
    ):
        note_obj = ComplaintNote(
            complaint_id=complaint_id,
            note=note,
            user_name=user_name,
            user_email=user_email,
            is_internal=is_internal
        )
        self.db.add(note_obj)
        self.db.commit()
        self.db.refresh(note_obj)
        return note_obj

    # -------------------------------------------------------------------------
    # ANALYTICS
    # -------------------------------------------------------------------------
    async def get_performance(
        self, supervisor_email: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        query = select(Complaint).where(Complaint.assigned_to_email == supervisor_email)
        if start_date:
            query = query.where(Complaint.created_at >= start_date)
        if end_date:
            query = query.where(Complaint.created_at <= end_date)

        result = self.db.execute(query)
        complaints = result.scalars().all()

        resolved = [c for c in complaints if c.status == "resolved"]
        avg_time = None
        if resolved:
            avg_time = sum(
                (c.resolved_at - c.created_at).total_seconds() for c in resolved if c.resolved_at
            ) / len(resolved) / 3600

        return {
            "supervisor_email": supervisor_email,
            "total_complaints": len(complaints),
            "resolved_complaints": len(resolved),
            "average_resolution_time_hours": round(avg_time, 2) if avg_time else None,
        }

    async def get_analytics(
        self,
        hostel_name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ):
        query = select(Complaint)
        if hostel_name:
            query = query.where(Complaint.hostel_name.ilike(f"%{hostel_name}%"))
        if start_date:
            query = query.where(Complaint.created_at >= start_date)
        if end_date:
            query = query.where(Complaint.created_at <= end_date)

        result = self.db.execute(query)
        complaints = result.scalars().all()

        total = len(complaints)
        category_counts = {}
        status_counts = {}

        for c in complaints:
            category_counts[c.category.value] = category_counts.get(c.category.value, 0) + 1
            status_counts[c.status.value] = status_counts.get(c.status.value, 0) + 1

        return {
            "total_complaints": total,
            "category_distribution": category_counts,
            "status_distribution": status_counts,
        }

    @staticmethod
    def get_statistics(db, hostel_ids, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """Return aggregated complaint statistics for the given hostel ids and date range.

        Note: complaints are linked to hostels by `hostel_name` in this schema,
        so we look up hostel names for the provided ids and filter complaints by name.
        """
        from app.models.complaint import Complaint
        from app.models.hostel import Hostel

        # Map hostel ids to hostel names
        hostel_names = []
        if hostel_ids:
            hostels = db.query(Hostel).filter(Hostel.id.in_(hostel_ids)).all()
            hostel_names = [h.hostel_name for h in hostels]

        query = db.query(Complaint)
        if hostel_names:
            query = query.filter(Complaint.hostel_name.in_(hostel_names))
        if start_date:
            query = query.filter(Complaint.created_at >= start_date)
        if end_date:
            query = query.filter(Complaint.created_at <= end_date)

        complaints = query.all()

        total = len(complaints)
        resolved_list = [c for c in complaints if c.resolved_at]
        resolved = len(resolved_list)

        avg_hours = 0.0
        if resolved_list:
            avg_hours = sum((c.resolved_at - c.created_at).total_seconds() for c in resolved_list) / len(resolved_list) / 3600
            avg_hours = round(avg_hours, 2)

        # Average student rating where available
        ratings = [c.student_rating for c in complaints if c.student_rating is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

        return {
            'total': total,
            'resolved': resolved,
            'average_resolution_hours': avg_hours,
            'average_rating': avg_rating
        }

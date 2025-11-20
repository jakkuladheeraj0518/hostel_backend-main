from sqlalchemy.orm import Session
from app.repositories.hostel_repository import HostelRepository
from app.schemas.super_admin_schemas import HostelUpsert
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

class HostelService:
    @staticmethod
    def upsert_hostel(db: Session, hostel_data: HostelUpsert) -> Dict[str, Any]:
        repo = HostelRepository(db)
        try:
            return repo.upsert_hostel(hostel_data)
        except ValueError as e:
            # Translate repository integrity errors into HTTP 400 responses
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def get_all_hostels(db: Session, skip: int = 0, limit: int = 100):
        repo = HostelRepository(db)
        return repo.get_all_hostels(skip, limit)

    @staticmethod
    def get_total_hostels_count(db: Session) -> int:
        repo = HostelRepository(db)
        return repo.get_total_hostels_count()

    @staticmethod
    def get_hostel_by_id(db: Session, hostel_id: int):
        repo = HostelRepository(db)
        return repo.get_hostel_by_id(hostel_id)

    @staticmethod
    def delete_hostel(db: Session, hostel_id: int):
        repo = HostelRepository(db)
        return repo.delete_hostel(hostel_id)

    @staticmethod
    def search_hostels(db: Session, search_term: str, skip: int = 0, limit: int = 100):
        repo = HostelRepository(db)
        return repo.search_hostels(search_term, skip, limit)

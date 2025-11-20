from typing import List
from sqlalchemy.orm import Session

from app.repositories.comparison_repository import get_hostel_comparison as repo_get_hostel_comparison
from app.models.hostel import Hostel
from app.models.rooms import Room


# ---------------------------------------------------------
# VERSION 1: (Simple repository pass-through)
# ---------------------------------------------------------
def compare_hostels(db: Session, hostel_ids: List[str]) -> List[dict]:
    return repo_get_hostel_comparison(db, hostel_ids)


# ---------------------------------------------------------
# VERSION 2: (Full comparison logic)
# ---------------------------------------------------------
class ComparisonService:

    @staticmethod
    def compare_hostels(db: Session, hostel_ids: list[int]):
        if len(hostel_ids) > 4:
            raise Exception("You can compare only up to 4 hostels")

        hostels = db.query(Hostel).filter(Hostel.id.in_(hostel_ids)).all()

        if not hostels:
            return []

        result = []

        for hostel in hostels:
            rooms = db.query(Room).filter(Room.hostel_id == hostel.id).all()

            result.append({
                "hostel_id": hostel.id,
                "name": hostel.name,
                "address": hostel.address,
                "amenities": hostel.amenities if hasattr(hostel, "amenities") else [],
                "pricing": [
                    {
                        "room_id": r.id,
                        "type": r.room_type,
                        "price": r.price if hasattr(r, "price") else None,
                        "available_beds": r.available_beds
                    }
                    for r in rooms
                ]
            })

        return result

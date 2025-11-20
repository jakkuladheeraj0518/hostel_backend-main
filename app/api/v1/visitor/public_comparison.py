from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import json

from app.dependencies import get_db
from app.models.hostel import Hostel
from app.models.rooms import Room

router = APIRouter(
    prefix="/visitor/compare",
    tags=["Hostel Comparison"]
)


@router.get("/")
def compare_hostels(
    hostel_ids: list[int] = Query(..., description="Provide up to 4 hostel IDs"),
    db: Session = Depends(get_db)
):
    """
    Compare up to 4 hostels and return essential details:
    - Basic info
    - Amenities
    - Pricing (min/max/average)
    - City / location
    - Room types
    - Availability summary
    - Computed hostel score
    """
    if not 1 <= len(hostel_ids) <= 4:
        raise HTTPException(
            status_code=400,
            detail="You must provide between 1 to 4 hostel IDs."
        )

    hostels = (
        db.query(Hostel)
        .filter(Hostel.id.in_(hostel_ids))
        .all()
    )

    if not hostels:
        raise HTTPException(
            status_code=404,
            detail="No hostels found for the given IDs."
        )

    response = []

    for hostel in hostels:

        # Fetch rooms of hostel
        rooms = db.query(Room).filter(Room.hostel_id == hostel.id).all()

        # -------------------------------
        # FIXED PRICING EXTRACTION LOGIC
        # -------------------------------
        prices = []
        for r in rooms:
            if r.monthly_price:
                prices.append(r.monthly_price)
            if r.quarterly_price:
                prices.append(r.quarterly_price)
            if r.annual_price:
                prices.append(r.annual_price)

        available_beds = sum(r.available_beds for r in rooms)
        available_rooms = len([r for r in rooms if r.available_beds > 0])

        # Convert amenities to list if stored as JSON/string
        amenities_list = []
        if hostel.amenities:
            try:
                amenities_list = json.loads(hostel.amenities)
                if isinstance(amenities_list, str):
                    amenities_list = amenities_list.split(",")
            except Exception:
                amenities_list = hostel.amenities.split(",")

        # Computed score
        hostel_score = 0
        if prices:
            hostel_score += 50
        if amenities_list:
            hostel_score += len(amenities_list) * 2
        if available_beds:
            hostel_score += min(available_beds, 20)

        hostel_data = {
            "id": hostel.id,
            "name": hostel.name,
            "city": hostel.city,
            "pincode": hostel.pincode,
            "description": hostel.description,
            "gender_type": hostel.gender_type,
            "amenities": amenities_list,

            # Pricing summary
            "min_price": min(prices) if prices else None,
            "max_price": max(prices) if prices else None,
            "avg_price": round(sum(prices) / len(prices), 2) if prices else None,

            # Rooms & Availability
            "total_rooms": len(rooms),
            "room_types": list({r.room_type.value for r in rooms}),
            "available_beds": available_beds,
            "available_rooms": available_rooms,

            # Scoring
            "hostel_score": hostel_score,

            # Dummy distance (until GPS added)
            "distance_dummy_km": 1.0,
        }

        response.append(hostel_data)

    return {
        "count": len(response),
        "hostels": response
    }

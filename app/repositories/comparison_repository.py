from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.rooms import Room
from app.models.beds import Bed, BedStatus


def get_hostel_comparison(db: Session, hostel_ids: List[str]) -> List[dict]:
    if not hostel_ids:
        return []

    pricing_rows = (
        db.query(
            Room.hostel_id.label("hostel_id"),
            func.min(Room.monthly_price).label("monthly_min"),
            func.avg(Room.monthly_price).label("monthly_avg"),
            func.max(Room.monthly_price).label("monthly_max"),
            func.min(Room.quarterly_price).label("quarterly_min"),
            func.avg(Room.quarterly_price).label("quarterly_avg"),
            func.max(Room.quarterly_price).label("quarterly_max"),
            func.min(Room.annual_price).label("annual_min"),
            func.avg(Room.annual_price).label("annual_avg"),
            func.max(Room.annual_price).label("annual_max"),
            func.count(Room.id).label("rooms_count"),
        )
        .filter(Room.hostel_id.in_(hostel_ids))
        .group_by(Room.hostel_id)
        .all()
    )

    pricing_map = {r.hostel_id: dict(r._mapping) for r in pricing_rows}

    amenities_map: dict[str, set[str]] = {hid: set() for hid in hostel_ids}
    amen_rows = db.query(Room.hostel_id, Room.amenities).filter(Room.hostel_id.in_(hostel_ids)).all()

    for hid, amen in amen_rows:
        if amen:
            parts = [a.strip() for a in amen.split(",") if a.strip()]
            amenities_map[hid].update(parts)

    bed_counts = (
        db.query(Bed.hostel_id, func.count(Bed.id))
        .filter(Bed.hostel_id.in_(hostel_ids))
        .group_by(Bed.hostel_id)
        .all()
    )
    bed_count_map = {hid: cnt for hid, cnt in bed_counts}

    available_beds = (
        db.query(Bed.hostel_id, func.count(Bed.id))
        .filter(
            Bed.hostel_id.in_(hostel_ids),
            Bed.bed_status == BedStatus.AVAILABLE
        )
        .group_by(Bed.hostel_id)
        .all()
    )
    available_beds_map = {hid: cnt for hid, cnt in available_beds}

    results = []

    for hid in hostel_ids:
        p = pricing_map.get(hid, {})

        results.append({
            "hostel_id": hid,
            "pricing": {
                "monthly_min": p.get("monthly_min"),
                "monthly_avg": float(p.get("monthly_avg")) if p.get("monthly_avg") else None,
                "monthly_max": p.get("monthly_max"),
                "quarterly_min": p.get("quarterly_min"),
                "quarterly_avg": float(p.get("quarterly_avg")) if p.get("quarterly_avg") else None,
                "quarterly_max": p.get("quarterly_max"),
                "annual_min": p.get("annual_min"),
                "annual_avg": float(p.get("annual_avg")) if p.get("annual_avg") else None,
                "annual_max": p.get("annual_max"),
            },
            "amenities": sorted(list(amenities_map.get(hid, set()))),
            "location": None,
            "rooms_count": int(p.get("rooms_count") or 0),
            "beds_count": int(bed_count_map.get(hid, 0)),
            "available_beds": int(available_beds_map.get(hid, 0)),
        })

    return results

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import exc as sa_exc

from app.models.rooms import Room, RoomType, MaintenanceStatus
from app.schemas.rooms import RoomCreate, RoomUpdate


def create_room(db: Session, room_in: RoomCreate) -> Room:
    obj = Room(**room_in.dict())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except sa_exc.ProgrammingError as e:
        db.rollback()
        raise RuntimeError("Database schema not initialized or table missing: " + str(e))
    except Exception:
        db.rollback()
        raise


def get_room(db: Session, room_id: UUID) -> Optional[Room]:
    return db.query(Room).filter(Room.id == room_id).first()


def list_rooms(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    room_type: Optional[RoomType] = None,
    maintenance_status: Optional[MaintenanceStatus] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_capacity: Optional[int] = None,
    only_available: Optional[bool] = None,
    amenities_like: Optional[str] = None,
) -> List[Room]:
    query = db.query(Room)
    if room_type is not None:
        query = query.filter(Room.room_type == room_type)
    if maintenance_status is not None:
        query = query.filter(Room.maintenance_status == maintenance_status)
    if min_capacity is not None:
        query = query.filter(Room.room_capacity >= min_capacity)
    if min_price is not None:
        query = query.filter(Room.monthly_price >= min_price)
    if max_price is not None:
        query = query.filter(Room.monthly_price <= max_price)
    if only_available:
        query = query.filter(Room.availability > 0)
    if amenities_like:
        like = f"%{amenities_like}%"
        query = query.filter(Room.amenities.ilike(like))

    return query.order_by(Room.id).offset(skip).limit(limit).all()


def update_room(db: Session, room: Room, room_in: RoomUpdate) -> Room:
    for field, value in room_in.dict(exclude_unset=True).items():
        setattr(room, field, value)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()


def set_room_maintenance(db: Session, room: Room, status: MaintenanceStatus) -> Room:
    room.maintenance_status = status
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def set_room_availability(db: Session, room: Room, availability: int) -> Room:
    room.availability = availability
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

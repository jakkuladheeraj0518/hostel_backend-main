from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.repositories.room_repository import (
    create_room as repo_create_room,
    get_room as repo_get_room,
    list_rooms as repo_list_rooms,
    update_room as repo_update_room,
    delete_room as repo_delete_room,
    set_room_maintenance as repo_set_room_maintenance,
    set_room_availability as repo_set_room_availability,
)
from app.schemas.rooms import RoomCreate, RoomUpdate
from app.models.rooms import Room, RoomType, MaintenanceStatus


def create_room(db: Session, room_in: RoomCreate) -> Room:
    return repo_create_room(db, room_in)


def get_room(db: Session, room_id: UUID) -> Optional[Room]:
    return repo_get_room(db, room_id)


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
    return repo_list_rooms(
        db,
        skip=skip,
        limit=limit,
        room_type=room_type,
        maintenance_status=maintenance_status,
        min_price=min_price,
        max_price=max_price,
        min_capacity=min_capacity,
        only_available=only_available,
        amenities_like=amenities_like,
    )


def update_room(db: Session, room_id, room_in: RoomUpdate) -> Optional[Room]:
    room = repo_get_room(db, room_id)
    if not room:
        return None
    return repo_update_room(db, room, room_in)


def delete_room(db: Session, room_id) -> bool:
    room = repo_get_room(db, room_id)
    if not room:
        return False
    repo_delete_room(db, room)
    return True


def set_room_maintenance(db: Session, room_id: int, status: MaintenanceStatus) -> Optional[Room]:
    room = repo_get_room(db, room_id)
    if not room:
        return None
    return repo_set_room_maintenance(db, room, status)


def set_room_availability(db: Session, room_id: int, availability: int) -> Optional[Room]:
    room = repo_get_room(db, room_id)
    if not room:
        return None
    return repo_set_room_availability(db, room, availability)

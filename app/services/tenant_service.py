"""
Multi-hostel admin validation
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from app.core.roles import Role
from app.repositories.hostel_repository import HostelRepository
from app.repositories.user_repository import UserRepository
from app.core.exceptions import InvalidHostelException


class TenantService:
    def __init__(self, db: Session):
        self.db = db
        self.hostel_repo = HostelRepository(db)
        self.user_repo = UserRepository(db)
    
    def validate_hostel_access(self, user_id: int, user_role: str, hostel_id: int) -> bool:
        """Validate if user has access to a hostel"""
        # Superadmin has access to all hostels
        if user_role == Role.SUPERADMIN:
            return True
        
        # Check if hostel exists
        hostel = self.hostel_repo.get_by_id(hostel_id)
        if not hostel:
            raise InvalidHostelException("Hostel not found")
        
        # For admin, check if assigned to hostel
        if user_role == Role.ADMIN:
            admin_hostels = self.hostel_repo.get_by_admin(user_id)
            hostel_ids = [h.id for h in admin_hostels]
            if hostel_id not in hostel_ids:
                raise InvalidHostelException("Admin not assigned to this hostel")
            return True
        
        # For other roles, check if user's hostel_id matches
        user = self.user_repo.get_by_id(user_id)
        if user and user.hostel_id == hostel_id:
            return True
        
        raise InvalidHostelException("User does not have access to this hostel")
    
    def get_user_hostels(self, user_id: int, user_role: str) -> List[dict]:
        """Get list of hostels user has access to"""
        if user_role == Role.SUPERADMIN:
            # Superadmin sees all hostels
            hostels = self.hostel_repo.get_all()
            return [{"id": h.id, "name": h.name, "address": h.address} for h in hostels]
        elif user_role == Role.ADMIN:
            # Admin sees assigned hostels
            hostels = self.hostel_repo.get_by_admin(user_id)
            return [{"id": h.id, "name": h.name, "address": h.address} for h in hostels]
        else:
            # Other roles see only their hostel
            user = self.user_repo.get_by_id(user_id)
            if user and user.hostel_id:
                hostel = self.hostel_repo.get_by_id(user.hostel_id)
                if hostel:
                    return [{"id": hostel.id, "name": hostel.name, "address": hostel.address}]
            return []
    
    def assign_admin_to_hostel(self, admin_id: int, hostel_id: int, assigner_role: str) -> dict:
        """Assign admin to hostel"""
        if assigner_role != Role.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superadmin can assign admins to hostels"
            )
        
        # Verify admin exists and is admin role
        admin = self.user_repo.get_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
        if admin.role != Role.ADMIN:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not an admin")
        
        # Verify hostel exists
        hostel = self.hostel_repo.get_by_id(hostel_id)
        if not hostel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found")
        
        # Assign
        mapping = self.hostel_repo.assign_admin(admin_id, hostel_id)
        return {
            "admin_id": mapping.admin_id,
            "hostel_id": mapping.hostel_id,
            "message": "Admin assigned to hostel successfully"
        }

    def assign_admin_to_hostels(self, admin_id: int, hostel_ids: List[int], assigner_role: str) -> dict:
        """Assign admin to multiple hostels (idempotent)

        Returns a summary with created and existing mappings.
        """
        if assigner_role != Role.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superadmin can assign admins to hostels"
            )

        admin = self.user_repo.get_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
        if admin.role != Role.ADMIN:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not an admin")

        created = []
        existing = []
        for hid in hostel_ids:
            hostel = self.hostel_repo.get_by_id(hid)
            if not hostel:
                # skip non-existent hostel ids
                continue
            # perform idempotent assignment
            self.hostel_repo.assign_admin(admin_id, hid)

        # After assignments, return the actual hostels assigned to the admin from the DB
        assigned_hostels = self.hostel_repo.get_by_admin(admin_id)
        assigned = [{"id": h.id, "name": h.name, "address": h.address} for h in assigned_hostels]

        return {
            "admin_id": admin_id,
            "assigned_hostels": assigned,
            "message": f"Assigned admin to {len(assigned)} hostels (idempotent)."
        }


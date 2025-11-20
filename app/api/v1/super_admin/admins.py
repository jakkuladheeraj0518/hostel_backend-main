from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import logging
from app.core.database import get_db
from app.repositories.admin_repository import AdminRepository
from app.services.admin_service import AdminService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from app.schemas.admin_schemas import (
    AdminCreate,
    AdminResponse,
    AdminHostelAssignmentCreate,
    AdminHostelAssignmentResponse,
    BulkAssignmentRequest,
    BulkAssignmentResponse,
    PermissionLevel
)

router = APIRouter(prefix="/admins", tags=["admins"])

def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(AdminRepository(db))

@router.post("/", response_model=AdminResponse)
async def create_admin(
    request: Request,
    admin: AdminCreate,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Create a new admin."""
    try:
        body = await request.json()
        logger.info(f"Creating admin with data: {body}")
        result = admin_service.create_admin(admin)
        logger.info(f"Admin created successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error creating admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[AdminResponse])
def get_all_admins(
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get all admins."""
    return admin_service.get_all_admins()

@router.get("/{admin_id}", response_model=AdminResponse)
def get_admin(
    admin_id: int,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get a specific admin by ID."""
    return admin_service.get_admin(admin_id)

@router.post("/{admin_id}/hostels", response_model=AdminHostelAssignmentResponse)
async def assign_hostel_to_admin(
    request: Request,
    admin_id: int,
    assignment: AdminHostelAssignmentCreate,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Assign a hostel to an admin with specific permission level."""
    try:
        body = await request.json()
        logger.info(f"Assigning hostel to admin {admin_id} with data: {body}")
        result = admin_service.assign_hostel(admin_id, assignment)
        logger.info(f"Hostel assignment created successfully: {result}")
        return result
    except Exception as e:
        logger.error(f"Error assigning hostel to admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/bulk-assign", response_model=BulkAssignmentResponse)
async def bulk_assign_hostels(
    request: Request,
    assignment: BulkAssignmentRequest,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Assign multiple hostels to an admin in bulk."""
    try:
        # Log the incoming request body
        body = await request.json()
        logger.info(f"Bulk assigning hostels with data: {body}")
        
        result = admin_service.bulk_assign_hostels(assignment)
        logger.info(f"Bulk assignment successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in bulk_assign_hostels endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{admin_id}/hostels", response_model=List[AdminHostelAssignmentResponse])
def get_admin_hostel_assignments(
    admin_id: int,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Get all hostel assignments for an admin."""
    return admin_service.get_admin_hostel_assignments(admin_id)

@router.put("/{admin_id}/hostels/{hostel_id}", response_model=AdminHostelAssignmentResponse)
def update_hostel_permission(
    admin_id: int,
    hostel_id: int,
    permission_level: PermissionLevel,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Update the permission level for a specific hostel assignment."""
    return admin_service.update_hostel_permission(admin_id, hostel_id, permission_level)

@router.delete("/{admin_id}/hostels/{hostel_id}")
def remove_hostel_assignment(
    admin_id: int,
    hostel_id: int,
    admin_service: AdminService = Depends(get_admin_service)
):
    """Remove a hostel assignment from an admin."""
    admin_service.remove_hostel_assignment(admin_id, hostel_id)
    return {"message": "Assignment removed successfully"}
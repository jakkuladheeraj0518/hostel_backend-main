from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories.admin_repository import AdminRepository
from app.schemas.admin_schemas import (
    AdminCreate,
    AdminResponse,
    AdminHostelAssignmentCreate,
    AdminHostelAssignmentResponse,
    BulkAssignmentRequest,
    BulkAssignmentResponse,
)
from app.models.admin import PermissionLevel

class AdminService:
    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository

    def create_admin(self, admin: AdminCreate) -> AdminResponse:
        # Check if admin with email already exists
        existing_admin = self.admin_repository.get_admin_by_email(admin.email)
        if existing_admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin with this email already exists"
            )
        
        db_admin = self.admin_repository.create_admin(admin)
        return AdminResponse.model_validate(db_admin)

    def get_admin(self, admin_id: int) -> AdminResponse:
        db_admin = self.admin_repository.get_admin(admin_id)
        if not db_admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
        return AdminResponse.model_validate(db_admin)

    def get_all_admins(self) -> List[AdminResponse]:
        db_admins = self.admin_repository.get_all_admins()
        return [AdminResponse.model_validate(admin) for admin in db_admins]

    def assign_hostel(
        self, admin_id: int, assignment: AdminHostelAssignmentCreate
    ) -> AdminHostelAssignmentResponse:
        import logging
        logger = logging.getLogger(__name__)
        
        # Log the input values
        logger.info(f"Assigning hostel with permission level: {assignment.permission_level} (type: {type(assignment.permission_level)})")
        
        # Verify admin exists
        if not self.admin_repository.get_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        # Create the assignment
        try:
            db_assignment = self.admin_repository.assign_hostel_to_admin(
                admin_id, assignment
            )
            return AdminHostelAssignmentResponse.model_validate(db_assignment)
        except Exception as e:
            logger.error(f"Error in assign_hostel: {str(e)}")
            raise

    def bulk_assign_hostels(
        self, assignment: BulkAssignmentRequest
    ) -> BulkAssignmentResponse:
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Verify admin exists
            if not self.admin_repository.get_admin(assignment.admin_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Admin not found"
                )
            
            logger.info(f"Bulk assigning with permission level: {assignment.permission_level} (type: {type(assignment.permission_level)})")
            
            # Convert permission_level to string if needed
            perm_level = assignment.permission_level
            if isinstance(perm_level, str):
                perm_level = PermissionLevel[perm_level.lower()]
            
            # Perform bulk assignment
            assignments = self.admin_repository.bulk_assign_hostels(
                assignment.admin_id,
                assignment.hostel_ids,
                perm_level
            )

            return BulkAssignmentResponse(
                success=True,
                message=f"Successfully assigned {len(assignments)} hostels to admin",
                assignments=[AdminHostelAssignmentResponse.model_validate(a) for a in assignments]
            )
        except Exception as e:
            logger.error(f"Error in bulk_assign_hostels: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_admin_hostel_assignments(
        self, admin_id: int
    ) -> List[AdminHostelAssignmentResponse]:
        # Verify admin exists
        if not self.admin_repository.get_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        assignments = self.admin_repository.get_admin_hostel_assignments(admin_id)
        return [AdminHostelAssignmentResponse.model_validate(a) for a in assignments]

    def update_hostel_permission(
        self, admin_id: int, hostel_id: int, permission_level: PermissionLevel
    ) -> AdminHostelAssignmentResponse:
        # Verify admin exists
        if not self.admin_repository.get_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        updated_assignment = self.admin_repository.update_hostel_permission(
            admin_id, hostel_id, permission_level
        )
        if not updated_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        return AdminHostelAssignmentResponse.model_validate(updated_assignment)

    def remove_hostel_assignment(self, admin_id: int, hostel_id: int) -> bool:
        # Verify admin exists
        if not self.admin_repository.get_admin(admin_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )

        success = self.admin_repository.remove_hostel_assignment(admin_id, hostel_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignment not found"
            )

        return True
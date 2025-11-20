from sqlalchemy.orm import Session
from sqlalchemy.sql import select
from typing import List, Optional
from app.models.admin import Admin, AdminHostelAssignment, PermissionLevel
from app.schemas.admin_schemas import AdminCreate, AdminHostelAssignmentCreate

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_admin(self, admin: AdminCreate) -> Admin:
        db_admin = Admin(**admin.model_dump())
        self.db.add(db_admin)
        self.db.commit()
        self.db.refresh(db_admin)
        return db_admin

    def get_admin(self, admin_id: int) -> Optional[Admin]:
        return self.db.query(Admin).filter(Admin.id == admin_id).first()

    def get_admin_by_email(self, email: str) -> Optional[Admin]:
        return self.db.query(Admin).filter(Admin.email == email).first()

    def get_all_admins(self) -> List[Admin]:
        return self.db.query(Admin).all()

    def update_admin(self, admin_id: int, admin_data: dict) -> Optional[Admin]:
        db_admin = self.get_admin(admin_id)
        if db_admin:
            for key, value in admin_data.items():
                setattr(db_admin, key, value)
            self.db.commit()
            self.db.refresh(db_admin)
        return db_admin

    def assign_hostel_to_admin(
        self, admin_id: int, assignment: AdminHostelAssignmentCreate
    ) -> AdminHostelAssignment:
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Ensure permission_level is in lowercase string format
            permission = assignment.permission_level.value if hasattr(assignment.permission_level, 'value') else str(assignment.permission_level).lower()
            
            db_assignment = AdminHostelAssignment(
                admin_id=admin_id,
                hostel_id=assignment.hostel_id,
                permission_level=permission
            )
            logger.info(f"Creating assignment with permission level: {permission}")
            
            self.db.add(db_assignment)
            self.db.commit()
            self.db.refresh(db_assignment)
            return db_assignment
        except Exception as e:
            logger.error(f"Error in assign_hostel_to_admin: {str(e)}")
            self.db.rollback()
            raise

    def bulk_assign_hostels(
        self, admin_id: int, hostel_ids: List[int], permission_level: PermissionLevel
    ) -> List[AdminHostelAssignment]:
        import logging
        logger = logging.getLogger(__name__)
        
        # Convert permission_level to string value to match the database enum type
        permission = permission_level.value if hasattr(permission_level, 'value') else str(permission_level).lower()
        
        # Use native SQL with ON CONFLICT DO UPDATE to handle existing assignments
        from sqlalchemy import text
        assignments = []
        for hostel_id in hostel_ids:
            stmt = text("""
                INSERT INTO admin_hostel_assignments (admin_id, hostel_id, permission_level)
                VALUES (:admin_id, :hostel_id, :permission_level)
                ON CONFLICT (admin_id, hostel_id) 
                DO UPDATE SET permission_level = :permission_level
                RETURNING *;
            """)
            
            result = self.db.execute(
                stmt,
                {
                    "admin_id": admin_id,
                    "hostel_id": hostel_id,
                    "permission_level": permission
                }
            )
            row = result.fetchone()
            
            # Convert the row to an AdminHostelAssignment model
            assignment = AdminHostelAssignment(
                id=row.id,
                admin_id=row.admin_id,
                hostel_id=row.hostel_id,
                permission_level=row.permission_level,
                assigned_at=row.assigned_at
            )
            assignments.append(assignment)
        
        self.db.commit()
        return assignments

    def get_admin_hostel_assignments(self, admin_id: int) -> List[AdminHostelAssignment]:
        return (
            self.db.query(AdminHostelAssignment)
            .filter(AdminHostelAssignment.admin_id == admin_id)
            .all()
        )

    def update_hostel_permission(
        self, admin_id: int, hostel_id: int, permission_level: PermissionLevel
    ) -> Optional[AdminHostelAssignment]:
        assignment = (
            self.db.query(AdminHostelAssignment)
            .filter(
                AdminHostelAssignment.admin_id == admin_id,
                AdminHostelAssignment.hostel_id == hostel_id
            )
            .first()
        )
        if assignment:
            assignment.permission_level = permission_level
            self.db.commit()
            self.db.refresh(assignment)
        return assignment

    def remove_hostel_assignment(self, admin_id: int, hostel_id: int) -> bool:
        result = (
            self.db.query(AdminHostelAssignment)
            .filter(
                AdminHostelAssignment.admin_id == admin_id,
                AdminHostelAssignment.hostel_id == hostel_id
            )
            .delete()
        )
        self.db.commit()
        return result > 0
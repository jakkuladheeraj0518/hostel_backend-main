"""
Seed RBAC matrix
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.permission import Permission, RolePermission
from app.core.permissions import Permission as Perm
from app.core.roles import Role


def seed_permissions():
    """Seed permissions and role-permission mappings"""
    db = SessionLocal()
    try:
        # Create permissions
        permissions_map = {
            Perm.CREATE_USER: "Create new users",
            Perm.READ_USER: "View users",
            Perm.UPDATE_USER: "Update user information",
            Perm.DELETE_USER: "Delete users",
            Perm.CREATE_HOSTEL: "Create new hostels",
            Perm.READ_HOSTEL: "View hostels",
            Perm.UPDATE_HOSTEL: "Update hostel information",
            Perm.DELETE_HOSTEL: "Delete hostels",
            Perm.SWITCH_SESSION: "Switch active hostel session",
            Perm.VIEW_SESSION: "View active session",
            Perm.VIEW_AUDIT: "View audit logs",
            Perm.CREATE_AUDIT: "Create audit log entries",
            Perm.EXPORT_AUDIT: "Export audit logs / reports",
            Perm.EXPORT_REPORTS: "Export various reports",
            Perm.MANAGE_SUBSCRIPTIONS: "Manage subscription plans and billing",
            Perm.VIEW_PAYMENTS: "View payments and transactions",
            Perm.MANAGE_PAYMENTS: "Manage payments and refunds",
            Perm.MANAGE_SUPERVISORS: "Create/assign/revoke hostel supervisors",
            Perm.MANAGE_HOSTEL_CONFIG: "Manage hostel configuration/settings",
            Perm.MANAGE_ATTENDANCE: "Manage attendance records",
            Perm.MANAGE_COMPLAINTS: "Manage complaints and tickets",
            Perm.MANAGE_MAINTENANCE: "Manage maintenance work orders",
            Perm.MANAGE_ANNOUNCEMENTS: "Manage hostel announcements",
            Perm.INITIATE_BOOKING: "Initiate booking process",
            Perm.CREATE_REGISTRATION: "Create user registrations",
            Perm.VIEW_OWN_PROFILE: "View own profile and personal data",
            Perm.VIEW_HOSTEL_ANNOUNCEMENTS: "View hostel announcements",
            Perm.MANAGE_PERMISSIONS: "Manage permissions",
            Perm.ASSIGN_ROLE: "Assign roles to users",
        }
        
        for perm_name, description in permissions_map.items():
            existing = db.query(Permission).filter(Permission.name == perm_name).first()
            if not existing:
                perm = Permission(
                    name=perm_name,
                    description=description,
                    resource=perm_name.split("_")[1] if "_" in perm_name else None,
                    action=perm_name.split("_")[0] if "_" in perm_name else None
                )
                db.add(perm)
        
        db.commit()
        print("Permissions seeded successfully")
        
        # Role-permission mappings are handled in app.core.permissions.PERMISSION_MATRIX
        # This can be extended to store in database if needed
        print("Role-permission mappings are defined in app.core.permissions.PERMISSION_MATRIX")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding permissions: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_permissions()


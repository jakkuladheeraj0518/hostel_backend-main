"""
🧩 RBAC permission matrix
"""
from typing import Dict, List, Set
from app.core.roles import Role, RoleHierarchy


class Permission:
    """Permission constants"""
    # User management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Hostel management
    CREATE_HOSTEL = "create_hostel"
    READ_HOSTEL = "read_hostel"
    UPDATE_HOSTEL = "update_hostel"
    DELETE_HOSTEL = "delete_hostel"
    
    # Session management
    SWITCH_SESSION = "switch_session"
    VIEW_SESSION = "view_session"
    
    # Audit
    VIEW_AUDIT = "view_audit"
    CREATE_AUDIT = "create_audit"
    # Export / reporting
    EXPORT_AUDIT = "export_audit"
    # Subscriptions & finance
    MANAGE_SUBSCRIPTIONS = "manage_subscriptions"
    VIEW_PAYMENTS = "view_payments"
    MANAGE_PAYMENTS = "manage_payments"

    # Supervisor and hostel management
    MANAGE_SUPERVISORS = "manage_supervisors"
    MANAGE_HOSTEL_CONFIG = "manage_hostel_config"

    # Day-to-day operations
    MANAGE_ATTENDANCE = "manage_attendance"
    MANAGE_COMPLAINTS = "manage_complaints"
    MANAGE_MAINTENANCE = "manage_maintenance"
    MANAGE_ANNOUNCEMENTS = "manage_announcements"

    # Booking / registration
    INITIATE_BOOKING = "initiate_booking"
    CREATE_REGISTRATION = "create_registration"

    # Broad reporting/export
    EXPORT_REPORTS = "export_reports"

    # Profile / announcements
    VIEW_OWN_PROFILE = "view_own_profile"
    VIEW_HOSTEL_ANNOUNCEMENTS = "view_hostel_announcements"
    
    # Permissions management
    MANAGE_PERMISSIONS = "manage_permissions"
    ASSIGN_ROLE = "assign_role"


# Role-Permission Matrix
PERMISSION_MATRIX: Dict[str, Set[str]] = {
    Role.SUPERADMIN: {
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.CREATE_HOSTEL,
        Permission.READ_HOSTEL,
        Permission.UPDATE_HOSTEL,
        Permission.DELETE_HOSTEL,
        Permission.SWITCH_SESSION,
        Permission.VIEW_SESSION,
        Permission.VIEW_AUDIT,
        Permission.CREATE_AUDIT,
        Permission.EXPORT_AUDIT,
        Permission.EXPORT_REPORTS,
        Permission.MANAGE_PERMISSIONS,
        Permission.ASSIGN_ROLE,
        Permission.MANAGE_SUBSCRIPTIONS,
        Permission.VIEW_PAYMENTS,
        Permission.MANAGE_PAYMENTS,
        Permission.MANAGE_HOSTEL_CONFIG,
        Permission.MANAGE_SUPERVISORS,
        Permission.MANAGE_ANNOUNCEMENTS,
        Permission.MANAGE_ATTENDANCE,
        Permission.MANAGE_COMPLAINTS,
        Permission.MANAGE_MAINTENANCE,
    },
    Role.ADMIN: {
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.READ_HOSTEL,
        Permission.SWITCH_SESSION,
        Permission.VIEW_SESSION,
        Permission.VIEW_AUDIT,
        Permission.CREATE_AUDIT,
        Permission.EXPORT_AUDIT,
        Permission.EXPORT_REPORTS,
        Permission.MANAGE_HOSTEL_CONFIG,
        Permission.MANAGE_SUPERVISORS,
        Permission.MANAGE_SUBSCRIPTIONS,
        Permission.VIEW_PAYMENTS,
        Permission.MANAGE_PAYMENTS,
        Permission.MANAGE_ANNOUNCEMENTS,
    },
    Role.SUPERVISOR: {
        Permission.READ_USER,
        Permission.READ_HOSTEL,
        Permission.VIEW_AUDIT,
        Permission.CREATE_AUDIT,
        Permission.MANAGE_ATTENDANCE,
        Permission.MANAGE_COMPLAINTS,
        Permission.MANAGE_MAINTENANCE,
        Permission.MANAGE_ANNOUNCEMENTS,
    },
    Role.STUDENT: {
        Permission.READ_USER,
        Permission.READ_HOSTEL,
        Permission.VIEW_OWN_PROFILE,
        Permission.VIEW_PAYMENTS,
        Permission.VIEW_HOSTEL_ANNOUNCEMENTS,
        Permission.INITIATE_BOOKING,
    },
    Role.VISITOR: {
        Permission.READ_USER,
        Permission.READ_HOSTEL,
        Permission.CREATE_REGISTRATION,
        Permission.INITIATE_BOOKING,
    },
}


def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission"""
    return permission in PERMISSION_MATRIX.get(role, set())


def get_role_permissions(role: str) -> Set[str]:
    """Get all permissions for a role"""
    return PERMISSION_MATRIX.get(role, set())


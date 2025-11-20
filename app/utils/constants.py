"""
Role & permission constants
"""
from app.core.roles import Role
from app.core.permissions import Permission

# Export all roles
ALL_ROLES = [role.value for role in Role]

# Export all permissions
ALL_PERMISSIONS = [
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
    Permission.MANAGE_PERMISSIONS,
    Permission.ASSIGN_ROLE,
    # Additional domain permissions
    Permission.EXPORT_AUDIT,
    Permission.EXPORT_REPORTS,
    Permission.MANAGE_SUBSCRIPTIONS,
    Permission.VIEW_PAYMENTS,
    Permission.MANAGE_PAYMENTS,
    Permission.MANAGE_SUPERVISORS,
    Permission.MANAGE_HOSTEL_CONFIG,
    Permission.MANAGE_ATTENDANCE,
    Permission.MANAGE_COMPLAINTS,
    Permission.MANAGE_MAINTENANCE,
    Permission.MANAGE_ANNOUNCEMENTS,
    Permission.INITIATE_BOOKING,
    Permission.CREATE_REGISTRATION,
    Permission.VIEW_OWN_PROFILE,
    Permission.VIEW_HOSTEL_ANNOUNCEMENTS,
]


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
    CREATE_COMPLAINT = "create_complaint"
    MANAGE_MAINTENANCE = "manage_maintenance"
    MANAGE_ANNOUNCEMENTS = "manage_announcements"
 
    # Multi-hostel & UI
    MULTI_HOSTEL_DASHBOARD = "multi_hostel_dashboard"
    SWITCH_HOSTEL = "switch_hostel"
    HOSTEL_SELECTOR = "hostel_selector"
 
    # Supervisor management & delegation
    ASSIGN_SUPERVISOR = "assign_supervisor"
    CONFIGURE_SUPERVISOR_PERMISSIONS = "configure_supervisor_permissions"
    OVERRIDE_SUPERVISOR = "override_supervisor"
 
    # Supervisor operational permissions
    SUPERVISOR_DASHBOARD_VIEW = "supervisor_dashboard_view"
    SUPERVISOR_RECORD_ATTENDANCE = "supervisor_record_attendance"
    SUPERVISOR_APPROVE_LEAVE = "supervisor_approve_leave"
    SUPERVISOR_CREATE_MAINTENANCE = "supervisor_create_maintenance"
    SUPERVISOR_ASSIGN_MAINTENANCE = "supervisor_assign_maintenance"
    SUPERVISOR_APPROVE_MAINTENANCE_WITHIN_LIMIT = "supervisor_approve_maintenance_within_limit"
    SUPERVISOR_ESCALATE_ISSUE = "supervisor_escalate_issue"
    SUPERVISOR_MODIFY_MENU = "supervisor_modify_menu"
    SUPERVISOR_CREATE_ANNOUNCEMENT = "supervisor_create_announcement"
    SUPERVISOR_VIEW_FINANCIALS_READONLY = "supervisor_view_financials_readonly"
    SUPERVISOR_UPDATE_STUDENT_CONTACT = "supervisor_update_student_contact"
    SUPERVISOR_VIEW_AUDIT = "supervisor_view_audit"
 
    # Hostel profile & room/booking management
    MANAGE_HOSTEL_LISTINGS = "manage_hostel_listings"
    MANAGE_ROOM_TYPES = "manage_room_types"
    MANAGE_BOOKINGS = "manage_bookings"
    DELETE_BOOKING = "delete_booking"
    MANAGE_WAITLIST = "manage_waitlist"
    MANAGE_STUDENTS = "manage_students"
 
    # Booking / registration
    INITIATE_BOOKING = "initiate_booking"
    CREATE_REGISTRATION = "create_registration"
 
    # Visitor / Booking actions
    BROWSE_PUBLIC_HOSTELS = "browse_public_hostels"
    VIEW_HOSTEL_DETAILS = "view_hostel_details"
    SUBMIT_PUBLIC_INQUIRY = "submit_public_inquiry"
    CREATE_BOOKING = "create_booking"
    VIEW_BOOKING = "view_booking"
    MODIFY_BOOKING = "modify_booking"
    CANCEL_BOOKING = "cancel_booking"
    DOWNLOAD_BOOKING_RECEIPT = "download_booking_receipt"
    SAVE_FAVOURITE_HOSTEL = "save_favourite_hostel"
    MANAGE_WISHLIST = "manage_wishlist"
    RATE_HOSTEL = "rate_hostel"
    WRITE_REVIEW = "write_review"
    VOTE_REVIEW = "vote_review"
    REQUEST_CALLBACK = "request_callback"
    NEGOTIATE_PRICE = "negotiate_price"
 
    # Broad reporting/export
    EXPORT_REPORTS = "export_reports"
    # Reporting & analytics
    VIEW_FINANCIAL_REPORTS = "view_financial_reports"
    VIEW_OPERATIONAL_REPORTS = "view_operational_reports"
    VIEW_MARKETING_REPORTS = "view_marketing_reports"
    VIEW_SUPERVISOR_PERFORMANCE = "view_supervisor_performance"
    VIEW_CONSOLIDATED_REPORTS = "view_consolidated_reports"
 
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
        Permission.CREATE_REGISTRATION,
        Permission.MANAGE_SUBSCRIPTIONS,
        Permission.VIEW_PAYMENTS,
        Permission.MANAGE_PAYMENTS,
        Permission.MANAGE_HOSTEL_CONFIG,
        Permission.MANAGE_SUPERVISORS,
        Permission.VIEW_FINANCIAL_REPORTS,
        Permission.VIEW_OPERATIONAL_REPORTS,
        Permission.VIEW_MARKETING_REPORTS,
        Permission.VIEW_SUPERVISOR_PERFORMANCE,
        Permission.VIEW_CONSOLIDATED_REPORTS,
        Permission.MULTI_HOSTEL_DASHBOARD,
        Permission.SWITCH_HOSTEL,
        Permission.HOSTEL_SELECTOR,
        Permission.ASSIGN_SUPERVISOR,
        Permission.CONFIGURE_SUPERVISOR_PERMISSIONS,
        Permission.OVERRIDE_SUPERVISOR,
        Permission.MANAGE_HOSTEL_LISTINGS,
        Permission.MANAGE_ROOM_TYPES,
        Permission.MANAGE_BOOKINGS,
        Permission.DELETE_BOOKING,
        Permission.MANAGE_WAITLIST,
        Permission.MANAGE_STUDENTS,
        Permission.MANAGE_ANNOUNCEMENTS,
        Permission.MANAGE_ATTENDANCE,
        Permission.MANAGE_COMPLAINTS,
        Permission.MANAGE_MAINTENANCE,
    },
    Role.ADMIN: {
        Permission.CREATE_USER,
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
        Permission.CREATE_REGISTRATION,
        Permission.VIEW_PAYMENTS,
        Permission.VIEW_FINANCIAL_REPORTS,
        Permission.VIEW_OPERATIONAL_REPORTS,
        Permission.VIEW_MARKETING_REPORTS,
        Permission.VIEW_SUPERVISOR_PERFORMANCE,
        Permission.VIEW_CONSOLIDATED_REPORTS,
        Permission.MANAGE_PAYMENTS,
        Permission.MANAGE_ANNOUNCEMENTS,
        Permission.MULTI_HOSTEL_DASHBOARD,
        Permission.SWITCH_HOSTEL,
        Permission.HOSTEL_SELECTOR,
        Permission.ASSIGN_SUPERVISOR,
        Permission.CONFIGURE_SUPERVISOR_PERMISSIONS,
        Permission.MANAGE_HOSTEL_LISTINGS,
        Permission.MANAGE_ROOM_TYPES,
        Permission.MANAGE_BOOKINGS,
        Permission.MANAGE_WAITLIST,
        Permission.MANAGE_STUDENTS,
    },
    Role.SUPERVISOR: {
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.READ_USER,
        Permission.READ_HOSTEL,
        Permission.VIEW_AUDIT,
        Permission.CREATE_AUDIT,
        Permission.MANAGE_ATTENDANCE,
        Permission.MANAGE_COMPLAINTS,
        Permission.MANAGE_MAINTENANCE,
        Permission.MANAGE_ANNOUNCEMENTS,
        # Supervisor operational rights (scoped to assigned hostel)
        Permission.SUPERVISOR_DASHBOARD_VIEW,
        Permission.SUPERVISOR_RECORD_ATTENDANCE,
        Permission.SUPERVISOR_APPROVE_LEAVE,
        Permission.SUPERVISOR_CREATE_MAINTENANCE,
        Permission.SUPERVISOR_ASSIGN_MAINTENANCE,
        Permission.SUPERVISOR_APPROVE_MAINTENANCE_WITHIN_LIMIT,
        Permission.SUPERVISOR_ESCALATE_ISSUE,
        Permission.SUPERVISOR_MODIFY_MENU,
        Permission.SUPERVISOR_CREATE_ANNOUNCEMENT,
        Permission.SUPERVISOR_VIEW_FINANCIALS_READONLY,
        Permission.SUPERVISOR_UPDATE_STUDENT_CONTACT,
        Permission.SUPERVISOR_VIEW_AUDIT,
        Permission.VIEW_SUPERVISOR_PERFORMANCE,
    },
    Role.STUDENT: {
        Permission.READ_USER,
        Permission.READ_HOSTEL,
        Permission.VIEW_OWN_PROFILE,
        Permission.CREATE_COMPLAINT,
        Permission.VIEW_PAYMENTS,
        Permission.VIEW_HOSTEL_ANNOUNCEMENTS,
        Permission.INITIATE_BOOKING,
        Permission.SAVE_FAVOURITE_HOSTEL,
        Permission.MANAGE_WISHLIST,
        Permission.RATE_HOSTEL,
        Permission.WRITE_REVIEW,
    },
    Role.VISITOR: {
        Permission.READ_USER,
        Permission.READ_HOSTEL,
        Permission.CREATE_REGISTRATION,
        Permission.INITIATE_BOOKING,
        Permission.BROWSE_PUBLIC_HOSTELS,
        Permission.VIEW_HOSTEL_DETAILS,
        Permission.SUBMIT_PUBLIC_INQUIRY,
        Permission.CREATE_BOOKING,
        Permission.VIEW_BOOKING,
        Permission.MODIFY_BOOKING,
        Permission.CANCEL_BOOKING,
        Permission.DOWNLOAD_BOOKING_RECEIPT,
        Permission.SAVE_FAVOURITE_HOSTEL,
        Permission.MANAGE_WISHLIST,
        Permission.RATE_HOSTEL,
        Permission.WRITE_REVIEW,
        Permission.VOTE_REVIEW,
        Permission.REQUEST_CALLBACK,
        Permission.NEGOTIATE_PRICE,
    },
}
 
 
def has_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission"""
    return permission in PERMISSION_MATRIX.get(role, set())
 
 
def get_role_permissions(role: str) -> Set[str]:
    """Get all permissions for a role"""
    return PERMISSION_MATRIX.get(role, set())
 
"""
Role constants & hierarchy
"""
from enum import Enum
from typing import Dict, List


class Role(str, Enum):
    """Role enumeration"""
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    STUDENT = "student"
    VISITOR = "visitor"


# Role hierarchy (higher number = more privileges)
RoleHierarchy: Dict[str, int] = {
    Role.SUPERADMIN: 5,
    Role.ADMIN: 4,
    Role.SUPERVISOR: 3,
    Role.STUDENT: 2,
    Role.VISITOR: 1,
}


def get_role_level(role: str) -> int:
    """Get hierarchy level of a role"""
    return RoleHierarchy.get(role, 0)


def can_manage_role(manager_role: str, target_role: str) -> bool:
    """Check if manager_role can manage target_role"""
    manager_level = get_role_level(manager_role)
    target_level = get_role_level(target_role)
    return manager_level > target_level


def get_all_roles() -> List[str]:
    """Get all available roles"""
    return [role.value for role in Role]


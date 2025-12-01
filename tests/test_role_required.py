from app.api.deps import role_required
from app.core.roles import Role
from app.core.exceptions import AccessDeniedException


class DummyUser:
    def __init__(self, role: str):
        self.role = role


def test_role_required_allows_enum_role_match():
    checker = role_required(Role.ADMIN, Role.SUPERVISOR)
    user = DummyUser('admin')
    # role_required should accept Enum members and succeed when role matches
    assert checker(current_user=user) is user


def test_role_required_allows_string_role_match():
    checker = role_required('admin', 'superadmin')
    user = DummyUser('admin')
    assert checker(current_user=user) is user


def test_role_required_denies_mismatch():
    checker = role_required(Role.SUPERADMIN)
    user = DummyUser('admin')
    try:
        checker(current_user=user)
        assert False, "Expected AccessDeniedException"
    except AccessDeniedException as e:
        assert 'Required roles' in str(e.detail)

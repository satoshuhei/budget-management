from __future__ import annotations

from app.domain.enums import Role


DUMMY_USERS: dict[str, dict[str, str]] = {
    "alice": {"password": "password", "role": Role.USER.value},
    "bob": {"password": "password", "role": Role.APPROVER.value},
    "admin": {"password": "admin", "role": Role.BUDGET_ADMIN.value},
    "auditor": {"password": "audit", "role": Role.AUDITOR.value},
}


def authenticate(username: str, password: str) -> Role | None:
    user = DUMMY_USERS.get(username)
    if not user:
        return None
    if user["password"] != password:
        return None
    return Role(user["role"])

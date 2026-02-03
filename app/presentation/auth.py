from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel

from app.domain.enums import Role


class CurrentUser(BaseModel):
    username: str
    role: Role


def get_current_user(
    x_user: str | None = Header(None, alias="X-User"),
    x_role: str | None = Header(None, alias="X-Role"),
) -> CurrentUser:
    if not x_user or not x_role:
        raise HTTPException(status_code=401, detail="Missing authentication headers")
    try:
        role = Role(x_role)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid role") from exc
    return CurrentUser(username=x_user, role=role)


def require_roles(*roles: Role):
    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return dependency

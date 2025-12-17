from dataclasses import dataclass

from fastapi import Header, HTTPException, status

@dataclass(frozen=True)
class CurrentUser:
    """Represents the current authenticated user."""
    user_id: int
    role: str # "employee", 'admin', 'manager'


def get_current_user(
    x_user_id: int = Header(..., alias="X-User-Id"),
    x_role: str = Header(..., alias="X-Role"),
) -> CurrentUser:
    role = x_role.strip().lower()
    if role not in {"employee", "manager", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "INVALID_ROLE", "message": "Invalid role header"},
        )
    return CurrentUser(user_id=x_user_id, role=role)

"""Role-based access control guard"""
def require_roles(*allowed: str):
    allowed_set = {r.lower() for r in allowed}

    def _guard(user: CurrentUser) -> CurrentUser:
        if user.role not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "INSUFFICIENT_PERMISSIONS",
                    "message": "You do not have permission to perform this action.",
                },
            )
        return user

    return _guard
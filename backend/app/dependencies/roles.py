from fastapi import Depends

from app.dependencies.auth import get_current_user
from app.exceptions.authorization import PermissionDeniedException
from app.models.user import User, UserRole


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Only allow administrators.
    """
    if current_user.role != UserRole.ADMIN:
        raise PermissionDeniedException()

    return current_user
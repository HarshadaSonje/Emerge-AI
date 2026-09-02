from fastapi import status

from app.exceptions.base import AppException


class PermissionDeniedException(AppException):
    def __init__(self):
        super().__init__(
            message="You do not have permission to perform this action.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHZ_001",
        )
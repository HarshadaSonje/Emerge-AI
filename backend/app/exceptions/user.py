from fastapi import status

from app.exceptions.base import AppException


class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            message="User not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="USER_001",
        )


class EmailAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="Email already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="USER_002",
        )
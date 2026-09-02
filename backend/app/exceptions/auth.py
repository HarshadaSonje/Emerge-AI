from fastapi import status

from app.exceptions.base import AppException


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid email or password.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_001",
        )


class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            message="Invalid or expired token.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_002",
        )


class InactiveUserException(AppException):
    def __init__(self):
        super().__init__(
            message="User account is inactive.",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTH_003",
        )
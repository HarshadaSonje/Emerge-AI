from fastapi import status

from app.exceptions.base import AppException


class EMSOrganizationNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            message="EMS Organization not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="EMS_001",
        )


class EMSOrganizationCodeExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="EMS Organization code already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="EMS_002",
        )


class EMSOrganizationEmailExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="EMS Organization email already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="EMS_003",
        )


class EMSOrganizationPhoneExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="EMS Organization phone already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="EMS_004",
        )
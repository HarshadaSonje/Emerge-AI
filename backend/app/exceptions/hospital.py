from fastapi import status

from app.exceptions.base import AppException


class HospitalNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            message="Hospital not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="HOSPITAL_001",
        )


class HospitalCodeExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="Hospital code already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="HOSPITAL_002",
        )


class HospitalEmailExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="Hospital email already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="HOSPITAL_003",
        )


class HospitalPhoneExistsException(AppException):
    def __init__(self):
        super().__init__(
            message="Hospital phone already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="HOSPITAL_004",
        )
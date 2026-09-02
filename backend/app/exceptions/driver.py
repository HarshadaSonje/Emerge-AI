from app.exceptions.base import AppException


class DriverNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            message="Driver not found.",
        )


class DriverAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="User already has a driver profile.",
        )


class LicenseNumberExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="License number already exists.",
        )


class InvalidLicenseException(AppException):
    def __init__(self):
        super().__init__(
            status_code=400,
            message="Driver license has expired.",
        )


class AmbulanceAlreadyAssignedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Ambulance is already assigned to another driver.",
        )
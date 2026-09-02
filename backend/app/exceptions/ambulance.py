from app.exceptions.base import AppException


class AmbulanceNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            message="Ambulance not found.",
            error_code="AMBULANCE_NOT_FOUND",
        )


class RegistrationNumberExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Registration number already exists.",
            error_code="REGISTRATION_NUMBER_EXISTS",
        )


class VehicleNumberExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Vehicle number already exists.",
            error_code="VEHICLE_NUMBER_EXISTS",
        )


class NoAvailableAmbulanceException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="No available ambulances.",
            error_code="NO_AVAILABLE_AMBULANCE",
        )


class NoAvailableAmbulanceWithDriverException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="No available ambulance with an available driver.",
            error_code="NO_AVAILABLE_AMBULANCE_WITH_DRIVER",
        )
from app.exceptions.base import AppException


class EmergencyCaseNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            error_code="EMERGENCY_CASE_NOT_FOUND",
            message="Emergency case not found.",
        )


class CaseNumberExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Case number already exists.",
        )
from app.exceptions.base import AppException


class DispatchAssignmentNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            message="Dispatch assignment not found.",
            error_code="DISPATCH_ASSIGNMENT_001",
        )


class AmbulanceAlreadyAssignedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Ambulance is already assigned to another active dispatch.",
            error_code="DISPATCH_ASSIGNMENT_002",
        )


class DriverAlreadyAssignedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Driver is already assigned to another active dispatch.",
            error_code="DISPATCH_ASSIGNMENT_003",
        )


class DispatchAlreadyCompletedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Dispatch has already been completed.",
            error_code="DISPATCH_ASSIGNMENT_004",
        )


class InvalidDispatchAssignmentStatusException(AppException):
    def __init__(self):
        super().__init__(
            status_code=400,
            message="Invalid dispatch assignment status transition.",
            error_code="DISPATCH_ASSIGNMENT_005",
        )


class DispatchAssignmentCannotBeDeletedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Dispatch assignment cannot be deleted in its current status.",
            error_code="DISPATCH_ASSIGNMENT_006",
        )
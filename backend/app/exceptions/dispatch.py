from app.exceptions.base import AppException


class DispatchNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            message="Dispatch not found.",
        )


class DispatchAlreadyCompletedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            error_code="DISPATCH_ALREADY_COMPLETED",
            message="Dispatch has already been completed.",
        )


class DispatchAlreadyCancelledException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Dispatch has already been cancelled.",
        )

class InvalidDispatchStatusException(AppException):
    def __init__(self):
        super().__init__(
            status_code=400,
            message="Invalid dispatch status transition.",
            error_code="DISPATCH_005",
        )
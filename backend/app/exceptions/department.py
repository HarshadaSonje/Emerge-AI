from app.exceptions.base import AppException


class DepartmentNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            message="Department not found.",
            error_code="DEPARTMENT_001",
        )


class DepartmentCodeExistsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=409,
            message="Department code already exists.",
            error_code="DEPARTMENT_002",
        )
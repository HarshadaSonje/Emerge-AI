from fastapi import status

from app.exceptions.base import AppException


class CityNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            message="City not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="CITY_001",
        )
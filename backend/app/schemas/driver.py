import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DriverBase(BaseModel):
    user_id: uuid.UUID
    ambulance_id: Optional[uuid.UUID] = None
    license_number: str
    license_expiry: date
    years_of_experience: int = Field(
        ge=0,
    )


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    ambulance_id: Optional[uuid.UUID] = None
    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    years_of_experience: Optional[int] = Field(
        default=None,
        ge=0,
    )


class DriverAvailabilityUpdate(BaseModel):
    is_available: bool


class DriverAmbulanceAssignment(BaseModel):
    ambulance_id: Optional[uuid.UUID]


class DriverResponse(DriverBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    is_available: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
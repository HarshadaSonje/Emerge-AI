import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.ambulance import (
    AmbulanceStatus,
    VehicleType,
)


class AmbulanceBase(BaseModel):
    registration_number: str
    vehicle_number: str
    vehicle_type: VehicleType
    hospital_id: uuid.UUID
    ems_organization_id: uuid.UUID
    current_latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )
    current_longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )


class AmbulanceCreate(AmbulanceBase):
    pass


class AmbulanceUpdate(BaseModel):
    registration_number: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    hospital_id: Optional[uuid.UUID] = None
    ems_organization_id: Optional[uuid.UUID] = None
    current_latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )
    current_longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )


class AmbulanceStatusUpdate(BaseModel):
    status: AmbulanceStatus


class AmbulanceLocationUpdate(BaseModel):
    current_latitude: float = Field(
        ge=-90,
        le=90,
    )
    current_longitude: float = Field(
        ge=-180,
        le=180,
    )


class AmbulanceResponse(AmbulanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: AmbulanceStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
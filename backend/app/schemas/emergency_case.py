import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.emergency_case import (
    EmergencyStatus,
    IncidentType,
    Severity,
)


class EmergencyCaseBase(BaseModel):
    reporter_name: str
    reporter_phone: str

    patient_name: Optional[str] = None
    patient_age: Optional[int] = Field(
        default=None,
        ge=0,
    )
    patient_gender: Optional[str] = None

    incident_type: IncidentType
    description: str

    latitude: float = Field(
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ge=-180,
        le=180,
    )

    address: str
    city_id: uuid.UUID


class EmergencyCaseCreate(EmergencyCaseBase):
    pass


class EmergencyCaseUpdate(BaseModel):
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None

    patient_name: Optional[str] = None
    patient_age: Optional[int] = Field(
        default=None,
        ge=0,
    )
    patient_gender: Optional[str] = None

    incident_type: Optional[IncidentType] = None
    description: Optional[str] = None

    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
    )

    address: Optional[str] = None
    city_id: Optional[uuid.UUID] = None


class EmergencyStatusUpdate(BaseModel):
    status: EmergencyStatus


class EmergencySeverityUpdate(BaseModel):
    severity: Severity


class EmergencyCaseResponse(EmergencyCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_number: str
    severity: Severity
    status: EmergencyStatus
    reported_at: datetime
    closed_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
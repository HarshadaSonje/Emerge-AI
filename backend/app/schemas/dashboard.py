from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.emergency_case import (
    EmergencyStatus,
    Severity,
)


class DashboardOverviewResponse(BaseModel):

    # Ambulances
    total_ambulances: int
    available_ambulances: int
    busy_ambulances: int
    maintenance_ambulances: int

    # Drivers
    total_drivers: int
    available_drivers: int

    # Hospitals
    total_hospitals: int

    # Departments
    total_departments: int

    # Emergency Cases
    active_emergencies: int
    completed_emergencies: int

    # Dispatches
    active_dispatches: int
    completed_dispatches: int


class RecentEmergencyResponse(BaseModel):
    id: UUID
    case_number: str
    patient_name: str | None
    incident_type: str
    severity: Severity
    status: EmergencyStatus
    reported_at: datetime

    model_config = {
        "from_attributes": True,
    }


class AmbulanceStatusSummaryResponse(BaseModel):
    status: str
    count: int


class EmergencyTrendResponse(BaseModel):
    date: date
    count: int
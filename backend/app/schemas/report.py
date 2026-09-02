from datetime import date

from pydantic import BaseModel
from uuid import UUID

class DailyReportResponse(BaseModel):
    date: date
    total_cases: int
    active_cases: int
    completed_cases: int
    critical_cases: int

class AmbulanceUtilizationResponse(BaseModel):
    ambulance_id: UUID
    registration_number: str
    vehicle_number: str
    status: str
    dispatch_count: int

class DriverPerformanceResponse(BaseModel):
    driver_id: UUID
    license_number: str
    years_of_experience: int
    is_available: bool
    dispatch_count: int

class HospitalWorkloadResponse(BaseModel):
    hospital_id: UUID
    hospital_name: str
    total_assignments: int
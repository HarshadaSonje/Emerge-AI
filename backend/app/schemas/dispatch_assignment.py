import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.dispatch_assignment import DispatchAssignmentStatus


class DispatchAssignmentCreate(BaseModel):
    dispatch_id: uuid.UUID
    ambulance_id: uuid.UUID
    driver_id: uuid.UUID
    hospital_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None


class DispatchAssignmentUpdate(BaseModel):
    ambulance_id: Optional[uuid.UUID] = None
    driver_id: Optional[uuid.UUID] = None
    hospital_id: Optional[uuid.UUID] = None
    remarks: Optional[str] = None


class DispatchAssignmentStatusUpdate(BaseModel):
    status: DispatchAssignmentStatus


class DispatchAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID

    dispatch_id: uuid.UUID
    ambulance_id: uuid.UUID
    driver_id: uuid.UUID
    hospital_id: Optional[uuid.UUID]

    status: DispatchAssignmentStatus

    assigned_at: datetime
    accepted_at: Optional[datetime]
    departed_at: Optional[datetime]
    arrived_scene_at: Optional[datetime]
    patient_loaded_at: Optional[datetime]
    arrived_hospital_at: Optional[datetime]
    completed_at: Optional[datetime]

    remarks: Optional[str]

    created_at: datetime
    updated_at: datetime
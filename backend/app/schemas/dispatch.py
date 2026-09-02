import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.dispatch import DispatchStatus


class DispatchCreate(BaseModel):
    incident_id: uuid.UUID
    dispatcher_id: uuid.UUID
    status: DispatchStatus = DispatchStatus.CREATED


class DispatchUpdate(BaseModel):
    status: Optional[DispatchStatus] = None


class DispatchStatusUpdate(BaseModel):
    status: DispatchStatus


class DispatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    incident_id: uuid.UUID
    dispatcher_id: uuid.UUID

    assigned_at: datetime
    status: DispatchStatus

    created_at: datetime
    updated_at: datetime
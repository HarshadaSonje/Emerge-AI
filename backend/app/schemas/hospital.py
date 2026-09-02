from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class HospitalBase(BaseModel):
    name: str
    code: str
    email: EmailStr
    phone: str
    address: str
    city_id: UUID
    ems_organization_id: UUID


class HospitalCreate(HospitalBase):
    pass


class HospitalUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    city_id: UUID | None = None
    ems_organization_id: UUID | None = None
    is_active: bool | None = None


class HospitalResponse(HospitalBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
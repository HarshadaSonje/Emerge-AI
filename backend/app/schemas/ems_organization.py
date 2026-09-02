import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EMSOrganizationCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=2, max_length=30)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    address: str = Field(..., min_length=5, max_length=255)
    city_id: uuid.UUID


class EMSOrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=150)
    code: str | None = Field(None, min_length=2, max_length=30)
    email: EmailStr | None = None
    phone: str | None = Field(None, min_length=10, max_length=20)
    address: str | None = Field(None, min_length=5, max_length=255)
    city_id: uuid.UUID | None = None
    is_active: bool | None = None


class EMSOrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    email: EmailStr
    phone: str
    address: str
    city_id: uuid.UUID
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )
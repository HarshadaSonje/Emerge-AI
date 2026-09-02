import uuid

from pydantic import BaseModel, ConfigDict, Field


class CityCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=2, max_length=100)


class CityUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    state: str | None = Field(None, min_length=2, max_length=100)
    country: str | None = Field(None, min_length=2, max_length=100)
    is_active: bool | None = None


class CityResponse(BaseModel):
    id: uuid.UUID
    name: str
    state: str
    country: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )
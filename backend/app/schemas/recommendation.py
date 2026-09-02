from uuid import UUID

from pydantic import BaseModel


class DispatchRecommendationResponse(BaseModel):
    ambulance_id: UUID
    driver_id: UUID
    hospital_id: UUID
    distance_km: float
    priority_score: int
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

from app.dependencies.auth import (
    get_current_user,
)

from app.models.user import User

from app.schemas.recommendation import (
    DispatchRecommendationResponse,
)

from app.services.recommendation_service import (
    RecommendationService,
)

router = APIRouter(
    prefix="/recommendation",
    tags=["Recommendation"],
)


@router.get(
    "/{emergency_case_id}",
    response_model=DispatchRecommendationResponse,
)
def recommend_dispatch(
    emergency_case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return RecommendationService.recommend_dispatch(
        db=db,
        emergency_case_id=emergency_case_id,
    )
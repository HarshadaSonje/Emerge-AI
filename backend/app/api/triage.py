import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.schemas.triage import TriageAssessment
from app.ai.services.triage_service import TriageService
from app.db.session import get_db


router = APIRouter(
    prefix="/triage",
    tags=["AI Triage"],
)


@router.post(
    "/{emergency_case_id}",
    response_model=TriageAssessment,
)
async def assess_triage(
    emergency_case_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return await TriageService.assess(
        db=db,
        emergency_case_id=emergency_case_id,
    )
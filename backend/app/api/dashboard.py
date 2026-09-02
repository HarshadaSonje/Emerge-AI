from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.dashboard import (
    AmbulanceStatusSummaryResponse,
    DashboardOverviewResponse,
    EmergencyTrendResponse,
    RecentEmergencyResponse,
)

from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardService.get_dashboard_overview(
        db=db,
    )

@router.get(
    "/recent-emergencies",
    response_model=list[RecentEmergencyResponse],
)
def get_recent_emergencies(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardService.get_recent_emergencies(
        db=db,
        limit=limit,
    )


@router.get(
    "/ambulance-status",
    response_model=list[AmbulanceStatusSummaryResponse],
)
def get_ambulance_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardService.get_ambulance_status_summary(
        db=db,
    )

@router.get(
    "/emergency-trends",
    response_model=list[EmergencyTrendResponse],
)
def get_emergency_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardService.get_emergency_trends(
        db=db,
    )
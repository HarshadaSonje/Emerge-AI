
from app.websocket.events import broadcast_event
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin
from app.models.user import User
from app.schemas.emergency_case import (
    EmergencyCaseCreate,
    EmergencyCaseResponse,
    EmergencyCaseUpdate,
    EmergencySeverityUpdate,
    EmergencyStatusUpdate,
)
from app.services.emergency_case_service import (
    EmergencyCaseService,
)
from uuid import UUID
from app.models.emergency_case import EmergencyStatus

router = APIRouter(
    prefix="/emergencies",
    tags=["Emergency Cases"],
)


@router.post(
    "",
    response_model=EmergencyCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_emergency_case(
    emergency_data: EmergencyCaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return EmergencyCaseService.create_emergency_case(
        db=db,
        emergency_data=emergency_data,
    )


@router.get(
    "",
    response_model=list[EmergencyCaseResponse],
)
def get_all_emergency_cases(
    page: int = 1,
    limit: int = 10,
    status: EmergencyStatus | None = None,
    city_id: UUID | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return EmergencyCaseService.get_all_emergency_cases(
        db=db,
        page=page,
        limit=limit,
        status=status,
        city_id=city_id,
        is_active=is_active,
    )


@router.get(
    "/{emergency_case_id}",
    response_model=EmergencyCaseResponse,
)
def get_emergency_case_by_id(
    emergency_case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return EmergencyCaseService.get_emergency_case_by_id(
        db=db,
        emergency_case_id=emergency_case_id,
    )


@router.put(
    "/{emergency_case_id}",
    response_model=EmergencyCaseResponse,
)
def update_emergency_case(
    emergency_case_id: UUID,
    emergency_data: EmergencyCaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return EmergencyCaseService.update_emergency_case(
        db=db,
        emergency_case_id=emergency_case_id,
        emergency_data=emergency_data,
    )


@router.patch(
    "/{emergency_case_id}/status",
    response_model=EmergencyCaseResponse,
)
async def update_status(
    emergency_case_id: UUID,
    status_data: EmergencyStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    emergency = EmergencyCaseService.update_status(
        db=db,
        emergency_case_id=emergency_case_id,
        status_data=status_data,
    )

    await broadcast_event(
        "EMERGENCY_STATUS_UPDATED",
        {
            "emergency_case_id": str(emergency.id),
            "status": emergency.status.value,
        },
    )

    return emergency


@router.patch(
    "/{emergency_case_id}/severity",
    response_model=EmergencyCaseResponse,
)
def update_severity(
    emergency_case_id: UUID,
    severity_data: EmergencySeverityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return EmergencyCaseService.update_severity(
        db=db,
        emergency_case_id=emergency_case_id,
        severity_data=severity_data,
    )


@router.patch(
    "/{emergency_case_id}/close",
    response_model=EmergencyCaseResponse,
)
def close_emergency_case(
    emergency_case_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return EmergencyCaseService.close_emergency_case(
        db=db,
        emergency_case_id=emergency_case_id,
    )
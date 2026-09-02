import uuid
from app.websocket.events import broadcast_event
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin
from app.models.user import User
from app.schemas.ambulance import (
    AmbulanceCreate,
    AmbulanceLocationUpdate,
    AmbulanceResponse,
    AmbulanceStatusUpdate,
    AmbulanceUpdate,
)
from app.services.ambulance_service import AmbulanceService

router = APIRouter(
    prefix="/ambulances",
    tags=["Ambulances"],
)


@router.post(
    "",
    response_model=AmbulanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ambulance(
    ambulance_data: AmbulanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Create ambulance.
    """
    return AmbulanceService.create_ambulance(
        db=db,
        ambulance_data=ambulance_data,
    )

@router.get(
    "",
    response_model=list[AmbulanceResponse],
)
def get_all_ambulances(
    page: int = 1,
    limit: int = 10,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return AmbulanceService.get_all_ambulances(
        db=db,
        page=page,
        limit=limit,
        status=status,
    )


@router.get(
    "/{ambulance_id}",
    response_model=AmbulanceResponse,
)
def get_ambulance_by_id(
    ambulance_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get ambulance by id.
    """
    return AmbulanceService.get_ambulance_by_id(
        db=db,
        ambulance_id=ambulance_id,
    )


@router.put(
    "/{ambulance_id}",
    response_model=AmbulanceResponse,
)
def update_ambulance(
    ambulance_id: uuid.UUID,
    ambulance_data: AmbulanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Update ambulance.
    """
    return AmbulanceService.update_ambulance(
        db=db,
        ambulance_id=ambulance_id,
        ambulance_data=ambulance_data,
    )


@router.patch(
    "/{ambulance_id}/activate",
    response_model=AmbulanceResponse,
)
def activate_ambulance(
    ambulance_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Activate ambulance.
    """
    return AmbulanceService.activate_ambulance(
        db=db,
        ambulance_id=ambulance_id,
    )


@router.patch(
    "/{ambulance_id}/deactivate",
    response_model=AmbulanceResponse,
)
def deactivate_ambulance(
    ambulance_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Deactivate ambulance.
    """
    return AmbulanceService.deactivate_ambulance(
        db=db,
        ambulance_id=ambulance_id,
    )


@router.patch(
    "/{ambulance_id}/status",
    response_model=AmbulanceResponse,
)
async def update_ambulance_status(
    ambulance_id: uuid.UUID,
    status_data: AmbulanceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Update ambulance status.
    """
    ambulance = AmbulanceService.update_status(
        db=db,
        ambulance_id=ambulance_id,
        status_data=status_data,
    )

    await broadcast_event(
        "AMBULANCE_STATUS_UPDATED",
        {
            "ambulance_id": str(ambulance.id),
            "status": ambulance.status.value,
        },
    )

    return ambulance


@router.patch(
    "/{ambulance_id}/location",
    response_model=AmbulanceResponse,
)
async def update_ambulance_location(
    ambulance_id: uuid.UUID,
    location_data: AmbulanceLocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ambulance = AmbulanceService.update_location(
        db=db,
        ambulance_id=ambulance_id,
        location_data=location_data,
    )

    await broadcast_event(
        "AMBULANCE_LOCATION_UPDATED",
        {
            "ambulance_id": str(ambulance.id),
            "latitude": ambulance.current_latitude,
            "longitude": ambulance.current_longitude,
        },
    )

    return ambulance
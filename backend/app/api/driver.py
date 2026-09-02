import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin
from app.models.user import User
from app.schemas.driver import (
    DriverAmbulanceAssignment,
    DriverAvailabilityUpdate,
    DriverCreate,
    DriverResponse,
    DriverUpdate,
)
from app.services.driver_service import DriverService

router = APIRouter(
    prefix="/drivers",
    tags=["Drivers"],
)


@router.post(
    "",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_driver(
    driver_data: DriverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DriverService.create_driver(
        db=db,
        driver_data=driver_data,
    )


@router.get(
    "",
    response_model=list[DriverResponse],
)
def get_all_drivers(
    page: int = 1,
    limit: int = 10,
    is_available: bool | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DriverService.get_all_drivers(
        db=db,
        page=page,
        limit=limit,
        is_available=is_available,
        is_active=is_active,
    )


@router.get(
    "/{driver_id}",
    response_model=DriverResponse,
)
def get_driver_by_id(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DriverService.get_driver_by_id(
        db=db,
        driver_id=driver_id,
    )


@router.put(
    "/{driver_id}",
    response_model=DriverResponse,
)
def update_driver(
    driver_id: uuid.UUID,
    driver_data: DriverUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DriverService.update_driver(
        db=db,
        driver_id=driver_id,
        driver_data=driver_data,
    )


@router.patch(
    "/{driver_id}/activate",
    response_model=DriverResponse,
)
def activate_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DriverService.activate_driver(
        db=db,
        driver_id=driver_id,
    )


@router.patch(
    "/{driver_id}/deactivate",
    response_model=DriverResponse,
)
def deactivate_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DriverService.deactivate_driver(
        db=db,
        driver_id=driver_id,
    )


@router.patch(
    "/{driver_id}/availability",
    response_model=DriverResponse,
)
def update_availability(
    driver_id: uuid.UUID,
    availability_data: DriverAvailabilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DriverService.update_availability(
        db=db,
        driver_id=driver_id,
        availability_data=availability_data,
    )


@router.patch(
    "/{driver_id}/assign-ambulance",
    response_model=DriverResponse,
)
def assign_ambulance(
    driver_id: uuid.UUID,
    assignment_data: DriverAmbulanceAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DriverService.assign_ambulance(
        db=db,
        driver_id=driver_id,
        assignment_data=assignment_data,
    )


@router.patch(
    "/{driver_id}/remove-ambulance",
    response_model=DriverResponse,
)
def remove_ambulance(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DriverService.remove_ambulance(
        db=db,
        driver_id=driver_id,
    )
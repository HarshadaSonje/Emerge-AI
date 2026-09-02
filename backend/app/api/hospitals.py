from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.roles import require_admin
from app.schemas.hospital import (
    HospitalCreate,
    HospitalResponse,
    HospitalUpdate,
)
from app.dependencies.auth import get_current_user
from app.services.hospital_service import HospitalService

router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"],
)
@router.post(
    "",
    response_model=HospitalResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return HospitalService.create_hospital(
        db,
        hospital_data,
    )
@router.get(
    "",
    response_model=list[HospitalResponse],
)
def get_all_hospitals(
    page: int = 1,
    limit: int = 10,
    city_id: UUID | None = None,
    ems_organization_id: UUID | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return HospitalService.get_all_hospitals(
        db=db,
        page=page,
        limit=limit,
        city_id=city_id,
        ems_organization_id=ems_organization_id,
        is_active=is_active,
    )
@router.get(
    "/{hospital_id}",
    response_model=HospitalResponse,
)
def get_hospital(
    hospital_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return HospitalService.get_hospital_by_id(
        db,
        hospital_id,
    )
@router.put(
    "/{hospital_id}",
    response_model=HospitalResponse,
)
def update_hospital(
    hospital_id: UUID,
    hospital_data: HospitalUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return HospitalService.update_hospital(
        db,
        hospital_id,
        hospital_data,
    )
@router.patch(
    "/{hospital_id}/activate",
    response_model=HospitalResponse,
)
def activate_hospital(
    hospital_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return HospitalService.activate_hospital(
        db,
        hospital_id,
    )
@router.patch(
    "/{hospital_id}/deactivate",
    response_model=HospitalResponse,
)
def deactivate_hospital(
    hospital_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return HospitalService.deactivate_hospital(
        db,
        hospital_id,
    )
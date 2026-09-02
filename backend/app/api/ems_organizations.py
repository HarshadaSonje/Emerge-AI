from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.roles import require_admin
from app.schemas.ems_organization import (
    EMSOrganizationCreate,
    EMSOrganizationResponse,
    EMSOrganizationUpdate,
)
from app.dependencies.auth import get_current_user
from app.services.ems_organization_service import EMSOrganizationService

router = APIRouter(
    prefix="/ems-organizations",
    tags=["EMS Organizations"],
)

@router.post(
    "",
    response_model=EMSOrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    organization_data: EMSOrganizationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return EMSOrganizationService.create_organization(
        db,
        organization_data,
    )
@router.get(
    "",
    response_model=list[EMSOrganizationResponse],
)
def get_all_organizations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return EMSOrganizationService.get_all_organizations(db)
@router.get(
    "/{organization_id}",
    response_model=EMSOrganizationResponse,
)
def get_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    return EMSOrganizationService.get_organization_by_id(
        db,
        organization_id,
    )
@router.put(
    "/{organization_id}",
    response_model=EMSOrganizationResponse,
)
def update_organization(
    organization_id: UUID,
    organization_data: EMSOrganizationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return EMSOrganizationService.update_organization(
        db,
        organization_id,
        organization_data,
    )
@router.patch(
    "/{organization_id}/activate",
    response_model=EMSOrganizationResponse,
)
def activate_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return EMSOrganizationService.activate_organization(
        db,
        organization_id,
    )
@router.patch(
    "/{organization_id}/deactivate",
    response_model=EMSOrganizationResponse,
)
def deactivate_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    return EMSOrganizationService.deactivate_organization(
        db,
        organization_id,
    )
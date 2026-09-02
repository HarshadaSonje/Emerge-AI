import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.city import (
    CityCreate,
    CityResponse,
    CityUpdate,
)
from app.services.city_service import CityService


router = APIRouter(
    prefix="/cities",
    tags=["Cities"],
)


@router.post(
    "",
    response_model=CityResponse,
)
def create_city(
    city_data: CityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CityService.create_city(
        db=db,
        city_data=city_data,
    )


@router.get(
    "",
    response_model=list[CityResponse],
)
def get_all_cities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CityService.get_all_cities(
        db=db,
    )


@router.get(
    "/{city_id}",
    response_model=CityResponse,
)
def get_city_by_id(
    city_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CityService.get_city_by_id(
        db=db,
        city_id=city_id,
    )


@router.put(
    "/{city_id}",
    response_model=CityResponse,
)
def update_city(
    city_id: uuid.UUID,
    city_data: CityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return CityService.update_city(
        db=db,
        city_id=city_id,
        city_data=city_data,
    )


@router.delete(
    "/{city_id}",
)
def delete_city(
    city_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    CityService.delete_city(
        db=db,
        city_id=city_id,
    )

    return {
        "message": "City deleted successfully."
    }
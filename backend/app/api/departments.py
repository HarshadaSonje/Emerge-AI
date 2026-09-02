from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin
from app.models.user import User
from app.schemas.department import (
    DepartmentCreate,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.department_service import DepartmentService

router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Create a new department.
    """
    return DepartmentService.create_department(
        db=db,
        department_data=department_data,
    )


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
def get_all_departments(
    page: int = 1,
    limit: int = 10,
    hospital_id: UUID | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return DepartmentService.get_all_departments(
        db=db,
        page=page,
        limit=limit,
        hospital_id=hospital_id,
        is_active=is_active,
    )


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def get_department_by_id(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get department by id.
    """
    return DepartmentService.get_department_by_id(
        db=db,
        department_id=department_id,
    )


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
)
def update_department(
    department_id: UUID,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Update department.
    """
    return DepartmentService.update_department(
        db=db,
        department_id=department_id,
        department_data=department_data,
    )


@router.patch(
    "/{department_id}/activate",
    response_model=DepartmentResponse,
)
def activate_department(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Activate department.
    """
    return DepartmentService.activate_department(
        db=db,
        department_id=department_id,
    )


@router.patch(
    "/{department_id}/deactivate",
    response_model=DepartmentResponse,
)
def deactivate_department(
    department_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Deactivate department.
    """
    return DepartmentService.deactivate_department(
        db=db,
        department_id=department_id,
    )
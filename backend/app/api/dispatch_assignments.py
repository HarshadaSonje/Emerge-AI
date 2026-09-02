from uuid import UUID
from app.websocket.events import broadcast_event

from app.models.dispatch_assignment import (
    DispatchAssignmentStatus,
)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin

from app.models.user import User

from app.schemas.dispatch_assignment import (
    DispatchAssignmentCreate,
    DispatchAssignmentResponse,
    DispatchAssignmentStatusUpdate,
    DispatchAssignmentUpdate,
)

from app.services.dispatch_assignment_service import (
    DispatchAssignmentService,
)

router = APIRouter(
    prefix="/dispatch-assignments",
    tags=["Dispatch Assignments"],
)
@router.post(
    "",
    response_model=DispatchAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    assignment_data: DispatchAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    assignment = DispatchAssignmentService.create_assignment(
        db=db,
        assignment_data=assignment_data,
    )

    await broadcast_event(
        "DISPATCH_ASSIGNMENT_CREATED",
        {
            "assignment_id": str(assignment.id),
            "dispatch_id": str(assignment.dispatch_id),
            "ambulance_id": str(assignment.ambulance_id),
            "driver_id": str(assignment.driver_id),
            "hospital_id": str(assignment.hospital_id) if assignment.hospital_id else None,
            "status": assignment.status.value,
        },
    )

    return assignment
@router.get(
    "",
    response_model=list[DispatchAssignmentResponse],
)
def get_all_assignments(
    page: int = 1,
    limit: int = 10,
    status: DispatchAssignmentStatus | None = None,
    ambulance_id: UUID | None = None,
    driver_id: UUID | None = None,
    hospital_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DispatchAssignmentService.get_all_assignments(
        db=db,
        page=page,
        limit=limit,
        status=status,
        ambulance_id=ambulance_id,
        driver_id=driver_id,
        hospital_id=hospital_id,
    )
@router.get(
    "/{assignment_id}",
    response_model=DispatchAssignmentResponse,
)
def get_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DispatchAssignmentService.get_assignment_by_id(
        db,
        assignment_id,
    )
@router.put(
    "/{assignment_id}",
    response_model=DispatchAssignmentResponse,
)
def update_assignment(
    assignment_id: UUID,
    assignment_data: DispatchAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return DispatchAssignmentService.update_assignment(
        db,
        assignment_id,
        assignment_data,
    )
@router.patch(
    "/{assignment_id}/status",
    response_model=DispatchAssignmentResponse,
)
async def update_status(
    assignment_id: UUID,
    status_data: DispatchAssignmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignment = DispatchAssignmentService.update_status(
        db,
        assignment_id,
        status_data,
    )

    await broadcast_event(
        "DISPATCH_ASSIGNMENT_STATUS_UPDATED",
        {
            "assignment_id": str(assignment.id),
            "dispatch_id": str(assignment.dispatch_id),
            "ambulance_id": str(assignment.ambulance_id),
            "driver_id": str(assignment.driver_id),
            "hospital_id": str(assignment.hospital_id) if assignment.hospital_id else None,
            "status": assignment.status.value,
        },
    )

    return assignment
@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assignment(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    DispatchAssignmentService.delete_assignment(
        db,
        assignment_id,
    )
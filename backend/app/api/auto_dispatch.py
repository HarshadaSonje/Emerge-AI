import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.roles import require_admin
from app.models.user import User
from app.services.auto_dispatch_service import AutoDispatchService
from app.websocket.events import broadcast_event


router = APIRouter(
    prefix="/auto-dispatch",
    tags=["Auto Dispatch"],
)


@router.post(
    "/{emergency_case_id}",
    status_code=status.HTTP_201_CREATED,
)
async def auto_dispatch(
    emergency_case_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    dispatch = await AutoDispatchService.auto_dispatch(
        db=db,
        emergency_case_id=emergency_case_id,
        dispatcher_id=current_user.id,
    )

    # =========================
    # Broadcast Dispatch Event
    # =========================

    await broadcast_event(
    "DISPATCH_CREATED",
    {
        "dispatch_id": str(dispatch.id),
        "incident_id": str(dispatch.incident_id),
        "dispatcher_id": str(dispatch.dispatcher_id),
        "status": dispatch.status,
    },
)

    # =========================
    # Get Created Assignment
    # =========================

    assignment = dispatch.assignments[0]

    # =========================
    # Broadcast Assignment Event
    # =========================

    await broadcast_event(
    "DISPATCH_ASSIGNMENT_CREATED",
    {
        "assignment_id": str(assignment.id),
        "dispatch_id": str(assignment.dispatch_id),
        "ambulance_id": str(assignment.ambulance_id),
        "driver_id": str(assignment.driver_id),
        "hospital_id": (
            str(assignment.hospital_id)
            if assignment.hospital_id
            else None
        ),
        "status": assignment.status,
    },
)

    return {
        "dispatch_id": str(dispatch.id),
        "incident_id": str(dispatch.incident_id),
        "assignment_id": str(assignment.id),
        "ambulance_id": str(assignment.ambulance_id),
        "driver_id": str(assignment.driver_id),
        "hospital_id": str(assignment.hospital_id) if assignment.hospital_id else None,
        "status": dispatch.status.value,
    }

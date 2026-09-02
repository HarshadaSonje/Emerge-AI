from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin

from app.models.dispatch import DispatchStatus
from app.models.user import User

from app.schemas.dispatch import (
    DispatchCreate,
    DispatchResponse,
    DispatchStatusUpdate,
    DispatchUpdate,
)

from app.services.dispatch_service import DispatchService
from app.websocket.events import broadcast_event


router = APIRouter(
    prefix="/dispatches",
    tags=["Dispatches"],
)


# ============================================================
# CREATE DISPATCH
# ============================================================

@router.post(
    "",
    response_model=DispatchResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dispatch(
    dispatch_data: DispatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    dispatch = DispatchService.create_dispatch(
        db=db,
        dispatch_data=dispatch_data,
    )

    await broadcast_event(
        "DISPATCH_CREATED",
        {
            "dispatch_id": str(dispatch.id),
            "incident_id": str(dispatch.incident_id),
            "status": dispatch.status.value,
        },
    )

    return dispatch


# ============================================================
# GET ALL DISPATCHES
# ============================================================

@router.get(
    "",
    response_model=list[DispatchResponse],
)
def get_all_dispatches(
    page: int = 1,
    limit: int = 10,
    status: DispatchStatus | None = None,
    dispatcher_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DispatchService.get_all_dispatches(
        db=db,
        page=page,
        limit=limit,
        status=status,
        dispatcher_id=dispatcher_id,
    )


# ============================================================
# GET SINGLE DISPATCH
# ============================================================

@router.get(
    "/{dispatch_id}",
    response_model=DispatchResponse,
)
def get_dispatch(
    dispatch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DispatchService.get_dispatch_by_id(
        db,
        dispatch_id,
    )


# ============================================================
# UPDATE DISPATCH
# ============================================================

@router.put(
    "/{dispatch_id}",
    response_model=DispatchResponse,
)
async def update_dispatch(
    dispatch_id: UUID,
    dispatch_data: DispatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    dispatch = DispatchService.update_dispatch(
        db,
        dispatch_id,
        dispatch_data,
    )

    await broadcast_event(
        "DISPATCH_UPDATED",
        {
            "dispatch_id": str(dispatch.id),
            "incident_id": str(dispatch.incident_id),
            "status": dispatch.status.value,
        },
    )

    return dispatch


# ============================================================
# UPDATE DISPATCH STATUS
# ============================================================

@router.patch(
    "/{dispatch_id}/status",
    response_model=DispatchResponse,
)
async def update_dispatch_status(
    dispatch_id: UUID,
    status_data: DispatchStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dispatch = DispatchService.update_status(
        db,
        dispatch_id,
        status_data,
    )

    await broadcast_event(
        "DISPATCH_STATUS_UPDATED",
        {
            "dispatch_id": str(dispatch.id),
            "incident_id": str(dispatch.incident_id),
            "status": dispatch.status.value,
        },
    )

    return dispatch


# ============================================================
# CANCEL DISPATCH
# ============================================================

@router.patch(
    "/{dispatch_id}/cancel",
    response_model=DispatchResponse,
)
async def cancel_dispatch(
    dispatch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    dispatch = DispatchService.cancel_dispatch(
        db,
        dispatch_id,
    )

    await broadcast_event(
        "DISPATCH_CANCELLED",
        {
            "dispatch_id": str(dispatch.id),
            "incident_id": str(dispatch.incident_id),
            "status": dispatch.status.value,
        },
    )

    return dispatch
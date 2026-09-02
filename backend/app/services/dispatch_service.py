import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.dispatch import (
    DispatchAlreadyCancelledException,
    DispatchAlreadyCompletedException,
    DispatchNotFoundException,
    InvalidDispatchStatusException,
)
from app.exceptions.emergency_case import EmergencyCaseNotFoundException
from app.exceptions.user import UserNotFoundException

from app.models.ambulance import (
    Ambulance,
    AmbulanceStatus,
)
from app.models.dispatch import (
    Dispatch,
    DispatchStatus,
)
from app.models.dispatch_assignment import (
    DispatchAssignment,
    DispatchAssignmentStatus,
)
from app.models.incident import Incident
from app.models.user import User

from app.schemas.dispatch import (
    DispatchCreate,
    DispatchStatusUpdate,
    DispatchUpdate,
)


class DispatchService:

    @staticmethod
    def create_dispatch(
        db: Session,
        dispatch_data: DispatchCreate,
    ) -> Dispatch:

        incident = db.get(
            Incident,
            dispatch_data.incident_id,
        )

        if incident is None:
            raise EmergencyCaseNotFoundException()

        dispatcher = db.get(
            User,
            dispatch_data.dispatcher_id,
        )

        if dispatcher is None:
            raise UserNotFoundException()

        dispatch = Dispatch(
            incident_id=dispatch_data.incident_id,
            dispatcher_id=dispatch_data.dispatcher_id,
            status=dispatch_data.status,
        )

        db.add(dispatch)
        db.commit()
        db.refresh(dispatch)

        return dispatch

    @staticmethod
    def get_all_dispatches(
        db: Session,
        page: int = 1,
        limit: int = 10,
        status: DispatchStatus | None = None,
        dispatcher_id: uuid.UUID | None = None,
    ) -> list[Dispatch]:

        query = select(Dispatch)

        if status is not None:
            query = query.where(
                Dispatch.status == status
            )

        if dispatcher_id is not None:
            query = query.where(
                Dispatch.dispatcher_id == dispatcher_id
            )

        query = (
            query
            .order_by(Dispatch.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(
            db.scalars(query).all()
        )

    @staticmethod
    def get_dispatch_by_id(
        db: Session,
        dispatch_id: uuid.UUID,
    ) -> Dispatch:

        dispatch = db.get(
            Dispatch,
            dispatch_id,
        )

        if dispatch is None:
            raise DispatchNotFoundException()

        return dispatch

    @staticmethod
    def update_dispatch(
        db: Session,
        dispatch_id: uuid.UUID,
        dispatch_data: DispatchUpdate,
    ) -> Dispatch:

        dispatch = db.get(
            Dispatch,
            dispatch_id,
        )

        if dispatch is None:
            raise DispatchNotFoundException()

        for field, value in dispatch_data.model_dump(
            exclude_unset=True,
        ).items():

            setattr(
                dispatch,
                field,
                value,
            )

        db.commit()
        db.refresh(dispatch)

        return dispatch

    @staticmethod
    def update_status(
        db: Session,
        dispatch_id: uuid.UUID,
        status_data: DispatchStatusUpdate,
    ) -> Dispatch:

        dispatch = db.get(
            Dispatch,
            dispatch_id,
        )

        if dispatch is None:
            raise DispatchNotFoundException()

        # =========================
        # Terminal Status Protection
        # =========================

        if dispatch.status == DispatchStatus.COMPLETED:
            raise DispatchAlreadyCompletedException()

        if dispatch.status == DispatchStatus.CANCELLED:
            raise DispatchAlreadyCancelledException()

        new_status = status_data.status

        # =========================
        # Validate Status Transition
        # =========================

        allowed_transitions = {
            DispatchStatus.CREATED: {
                DispatchStatus.ACCEPTED,
                DispatchStatus.CANCELLED,
            },
            DispatchStatus.ACCEPTED: {
                DispatchStatus.EN_ROUTE,
                DispatchStatus.CANCELLED,
            },
            DispatchStatus.EN_ROUTE: {
                DispatchStatus.COMPLETED,
                DispatchStatus.CANCELLED,
            },
        }

        allowed_statuses = allowed_transitions.get(
            dispatch.status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise InvalidDispatchStatusException()

        # =========================
        # Find Assignment
        # =========================

        assignment = db.scalar(
            select(DispatchAssignment).where(
                DispatchAssignment.dispatch_id
                == dispatch.id
            )
        )

        # =========================
        # Update Dispatch
        # =========================

        dispatch.status = new_status

        # =========================
        # Synchronize Assignment
        # =========================

        if assignment is not None:

            if new_status == DispatchStatus.ACCEPTED:

                assignment.status = (
                    DispatchAssignmentStatus.ACCEPTED
                )

            elif new_status == DispatchStatus.EN_ROUTE:

                assignment.status = (
                    DispatchAssignmentStatus.EN_ROUTE
                )

            elif new_status == DispatchStatus.COMPLETED:

                assignment.status = (
                    DispatchAssignmentStatus.COMPLETED
                )

            elif new_status == DispatchStatus.CANCELLED:

                assignment.status = (
                    DispatchAssignmentStatus.CANCELLED
                )

            # =========================
            # Synchronize Ambulance
            # =========================

            if assignment.ambulance_id is not None:

                ambulance = db.get(
                    Ambulance,
                    assignment.ambulance_id,
                )

                if ambulance is not None:

                    if new_status == DispatchStatus.ACCEPTED:

                        ambulance.status = (
                            AmbulanceStatus.DISPATCHED
                        )

                    elif new_status == DispatchStatus.EN_ROUTE:

                        ambulance.status = (
                            AmbulanceStatus.ON_ROUTE
                        )

                    elif new_status == DispatchStatus.COMPLETED:

                        ambulance.status = (
                            AmbulanceStatus.AVAILABLE
                        )

                        ambulance.is_available = True

                    elif new_status == DispatchStatus.CANCELLED:

                        ambulance.status = (
                            AmbulanceStatus.AVAILABLE
                        )

                        ambulance.is_available = True

            # =========================
            # Synchronize Driver
            # =========================

            if assignment.driver_id is not None:

                driver = assignment.driver

                if driver is not None:

                    if new_status == DispatchStatus.COMPLETED:

                        driver.is_available = True

                    elif new_status == DispatchStatus.CANCELLED:

                        driver.is_available = True

                    elif new_status in (
                        DispatchStatus.ACCEPTED,
                        DispatchStatus.EN_ROUTE,
                    ):

                        driver.is_available = False

        # =========================
        # Synchronize Incident
        # =========================

        incident = dispatch.incident

        if incident is not None:

            incident.status = new_status.value

        # =========================
        # Commit Everything
        # =========================

        db.commit()
        db.refresh(dispatch)

        return dispatch

    @staticmethod
    def cancel_dispatch(
        db: Session,
        dispatch_id: uuid.UUID,
    ) -> Dispatch:

        dispatch = db.get(
            Dispatch,
            dispatch_id,
        )

        if dispatch is None:
            raise DispatchNotFoundException()

        if dispatch.status == DispatchStatus.COMPLETED:
            raise DispatchAlreadyCompletedException()

        if dispatch.status == DispatchStatus.CANCELLED:
            raise DispatchAlreadyCancelledException()

        # =========================
        # Update Dispatch
        # =========================

        dispatch.status = DispatchStatus.CANCELLED

        # =========================
        # Find Assignment
        # =========================

        assignment = db.scalar(
            select(DispatchAssignment).where(
                DispatchAssignment.dispatch_id
                == dispatch.id
            )
        )

        if assignment is not None:

            # Update assignment
            assignment.status = (
                DispatchAssignmentStatus.CANCELLED
            )

            # Update ambulance
            ambulance = db.get(
                Ambulance,
                assignment.ambulance_id,
            )

            if ambulance is not None:

                ambulance.status = (
                    AmbulanceStatus.AVAILABLE
                )

                ambulance.is_available = True

            # Update driver
            driver = assignment.driver

            if driver is not None:
                driver.is_available = True

        # =========================
        # Update Incident
        # =========================

        incident = dispatch.incident

        if incident is not None:

            incident.status = (
                DispatchStatus.CANCELLED.value
            )

        # =========================
        # Commit
        # =========================

        db.commit()
        db.refresh(dispatch)

        return dispatch
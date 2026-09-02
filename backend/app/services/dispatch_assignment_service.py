import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.ambulance import AmbulanceNotFoundException
from app.exceptions.dispatch import DispatchNotFoundException
from app.exceptions.dispatch_assignment import (
    AmbulanceAlreadyAssignedException,
    DispatchAssignmentCannotBeDeletedException,
    DispatchAssignmentNotFoundException,
    DriverAlreadyAssignedException,
    InvalidDispatchAssignmentStatusException,
)
from app.exceptions.driver import DriverNotFoundException
from app.exceptions.hospital import HospitalNotFoundException

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
from app.models.emergency_case import EmergencyStatus
from app.models.driver import Driver
from app.models.hospital import Hospital

from app.schemas.dispatch_assignment import (
    DispatchAssignmentCreate,
    DispatchAssignmentStatusUpdate,
    DispatchAssignmentUpdate,
)


class DispatchAssignmentService:

    @staticmethod
    def get_assignment_or_raise(
        db: Session,
        assignment_id: uuid.UUID,
    ) -> DispatchAssignment:

        assignment = db.get(
            DispatchAssignment,
            assignment_id,
        )

        if assignment is None:
            raise DispatchAssignmentNotFoundException()

        return assignment

    @staticmethod
    def create_assignment(
        db: Session,
        assignment_data: DispatchAssignmentCreate,
    ) -> DispatchAssignment:

        dispatch = db.get(
            Dispatch,
            assignment_data.dispatch_id,
        )

        if dispatch is None:
            raise DispatchNotFoundException()

        ambulance = db.get(
            Ambulance,
            assignment_data.ambulance_id,
        )

        if ambulance is None:
            raise AmbulanceNotFoundException()

        driver = db.get(
            Driver,
            assignment_data.driver_id,
        )

        if driver is None:
            raise DriverNotFoundException()

        if assignment_data.hospital_id:

            hospital = db.get(
                Hospital,
                assignment_data.hospital_id,
            )

            if hospital is None:
                raise HospitalNotFoundException()

        # Ambulance availability is determined by its status.
        if ambulance.status != AmbulanceStatus.AVAILABLE:
            raise AmbulanceAlreadyAssignedException()

        if not driver.is_available:
            raise DriverAlreadyAssignedException()

        assignment = DispatchAssignment(
            dispatch_id=assignment_data.dispatch_id,
            ambulance_id=assignment_data.ambulance_id,
            driver_id=assignment_data.driver_id,
            hospital_id=assignment_data.hospital_id,
            remarks=assignment_data.remarks,
        )

        ambulance.status = AmbulanceStatus.DISPATCHED

        driver.is_available = False

        db.add(assignment)

        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def get_all_assignments(
        db: Session,
        page: int = 1,
        limit: int = 10,
        status: DispatchAssignmentStatus | None = None,
        ambulance_id: uuid.UUID | None = None,
        driver_id: uuid.UUID | None = None,
        hospital_id: uuid.UUID | None = None,
    ) -> list[DispatchAssignment]:

        query = select(DispatchAssignment)

        if status is not None:
            query = query.where(
                DispatchAssignment.status == status
            )

        if ambulance_id is not None:
            query = query.where(
                DispatchAssignment.ambulance_id == ambulance_id
            )

        if driver_id is not None:
            query = query.where(
                DispatchAssignment.driver_id == driver_id
            )

        if hospital_id is not None:
            query = query.where(
                DispatchAssignment.hospital_id == hospital_id
            )

        query = (
            query
            .order_by(
                DispatchAssignment.created_at.desc()
            )
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(
            db.scalars(query).all()
        )

    @staticmethod
    def get_assignment_by_id(
        db: Session,
        assignment_id: uuid.UUID,
    ) -> DispatchAssignment:

        return DispatchAssignmentService.get_assignment_or_raise(
            db,
            assignment_id,
        )

    @staticmethod
    def update_assignment(
        db: Session,
        assignment_id: uuid.UUID,
        assignment_data: DispatchAssignmentUpdate,
    ) -> DispatchAssignment:

        assignment = (
            DispatchAssignmentService.get_assignment_or_raise(
                db,
                assignment_id,
            )
        )

        for field, value in assignment_data.model_dump(
            exclude_unset=True
        ).items():

            setattr(
                assignment,
                field,
                value,
            )

        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def update_status(
        db: Session,
        assignment_id: uuid.UUID,
        status_data: DispatchAssignmentStatusUpdate,
    ) -> DispatchAssignment:

        assignment = (
            DispatchAssignmentService.get_assignment_or_raise(
                db,
                assignment_id,
            )
        )

        new_status = status_data.status

        now = datetime.now(timezone.utc)

        # =========================
        # Validate Status Transition
        # =========================

        allowed_transitions = {
            DispatchAssignmentStatus.ASSIGNED: {
                DispatchAssignmentStatus.ACCEPTED,
                DispatchAssignmentStatus.CANCELLED,
            },

            DispatchAssignmentStatus.ACCEPTED: {
                DispatchAssignmentStatus.EN_ROUTE,
                DispatchAssignmentStatus.CANCELLED,
            },

            DispatchAssignmentStatus.EN_ROUTE: {
                DispatchAssignmentStatus.ARRIVED_AT_SCENE,
                DispatchAssignmentStatus.CANCELLED,
            },

            DispatchAssignmentStatus.ARRIVED_AT_SCENE: {
                DispatchAssignmentStatus.PATIENT_ONBOARD,
                DispatchAssignmentStatus.CANCELLED,
            },

            DispatchAssignmentStatus.PATIENT_ONBOARD: {
                DispatchAssignmentStatus.ARRIVED_AT_HOSPITAL,
                DispatchAssignmentStatus.CANCELLED,
            },

            DispatchAssignmentStatus.ARRIVED_AT_HOSPITAL: {
                DispatchAssignmentStatus.COMPLETED,
            },

            DispatchAssignmentStatus.COMPLETED: set(),

            DispatchAssignmentStatus.CANCELLED: set(),
        }

        allowed_statuses = allowed_transitions.get(
            assignment.status,
            set(),
        )

        if new_status not in allowed_statuses:
            raise InvalidDispatchAssignmentStatusException()

        # =========================
        # Update Assignment Status
        # =========================

        assignment.status = new_status

        # =========================
        # Synchronize Parent Dispatch
        # =========================

        dispatch = assignment.dispatch

        if dispatch is not None:

            if new_status == DispatchAssignmentStatus.ACCEPTED:

                dispatch.status = DispatchStatus.ACCEPTED

            elif new_status == DispatchAssignmentStatus.EN_ROUTE:

                dispatch.status = DispatchStatus.EN_ROUTE

            elif new_status in (
                DispatchAssignmentStatus.ARRIVED_AT_SCENE,
                DispatchAssignmentStatus.PATIENT_ONBOARD,
                DispatchAssignmentStatus.ARRIVED_AT_HOSPITAL,
            ):

                dispatch.status = DispatchStatus.EN_ROUTE

            elif new_status == DispatchAssignmentStatus.COMPLETED:

                dispatch.status = DispatchStatus.COMPLETED

            elif new_status == DispatchAssignmentStatus.CANCELLED:

                dispatch.status = DispatchStatus.CANCELLED

        # =========================
        # Synchronize Incident
        # =========================

        incident = (
            dispatch.incident
            if dispatch is not None
            else None
        )

        if incident is not None:

            if new_status == DispatchAssignmentStatus.COMPLETED:

                incident.status = (
                    EmergencyStatus.COMPLETED.value
                )

                incident.is_active = False

            elif new_status == DispatchAssignmentStatus.CANCELLED:

                incident.status = (
                    EmergencyStatus.CANCELLED.value
                )

                incident.is_active = False

        # =========================
        # Synchronize Emergency Case
        # =========================

        if incident is not None:

            emergency_case = incident.emergency_case

            if emergency_case is not None:

                if new_status == DispatchAssignmentStatus.COMPLETED:

                    emergency_case.status = (
                        EmergencyStatus.COMPLETED
                    )

                    emergency_case.closed_at = now

                    emergency_case.is_active = False

                elif new_status == DispatchAssignmentStatus.CANCELLED:

                    emergency_case.status = (
                        EmergencyStatus.CANCELLED
                    )

                    emergency_case.closed_at = now

                    emergency_case.is_active = False

        # =========================
        # Status Lifecycle
        # =========================

        if new_status == DispatchAssignmentStatus.ACCEPTED:

            assignment.accepted_at = now

            assignment.ambulance.status = (
                AmbulanceStatus.DISPATCHED
            )

            assignment.driver.is_available = False

        elif new_status == DispatchAssignmentStatus.EN_ROUTE:

            assignment.departed_at = now

            assignment.ambulance.status = (
                AmbulanceStatus.ON_ROUTE
            )

            assignment.driver.is_available = False

        elif new_status == DispatchAssignmentStatus.ARRIVED_AT_SCENE:

            assignment.arrived_scene_at = now

            assignment.ambulance.status = (
                AmbulanceStatus.AT_SCENE
            )

            assignment.driver.is_available = False

        elif new_status == DispatchAssignmentStatus.PATIENT_ONBOARD:

            assignment.patient_loaded_at = now

            assignment.ambulance.status = (
                AmbulanceStatus.TRANSPORTING
            )

            assignment.driver.is_available = False

        elif new_status == DispatchAssignmentStatus.ARRIVED_AT_HOSPITAL:

            assignment.arrived_hospital_at = now

            assignment.ambulance.status = (
                AmbulanceStatus.AT_HOSPITAL
            )

            assignment.driver.is_available = False

        elif new_status == DispatchAssignmentStatus.COMPLETED:

            assignment.completed_at = now

            assignment.ambulance.status = (
                AmbulanceStatus.AVAILABLE
            )

            assignment.driver.is_available = True

        elif new_status == DispatchAssignmentStatus.CANCELLED:

            assignment.ambulance.status = (
                AmbulanceStatus.AVAILABLE
            )

            assignment.driver.is_available = True

        # =========================
        # Commit Everything Together
        # =========================

        db.commit()
        db.refresh(assignment)

        return assignment

    @staticmethod
    def delete_assignment(
        db: Session,
        assignment_id: uuid.UUID,
    ) -> None:

        assignment = (
            DispatchAssignmentService.get_assignment_or_raise(
                db,
                assignment_id,
            )
        )

        # Only an untouched ASSIGNED record may be deleted.
        if assignment.status != DispatchAssignmentStatus.ASSIGNED:
            raise DispatchAssignmentCannotBeDeletedException()

        assignment.ambulance.status = (
            AmbulanceStatus.AVAILABLE
        )

        assignment.driver.is_available = True

        db.delete(assignment)

        db.commit()
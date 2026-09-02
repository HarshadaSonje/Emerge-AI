import uuid

from sqlalchemy.orm import Session

from app.ai.services.triage_service import TriageService

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
from app.models.driver import Driver
from app.models.emergency_case import (
    EmergencyCase,
    EmergencyStatus,
)
from app.models.incident import Incident

from app.services.recommendation_service import (
    RecommendationService,
)


class AutoDispatchService:

    @staticmethod
    async def auto_dispatch(
        db: Session,
        emergency_case_id: uuid.UUID,
        dispatcher_id: uuid.UUID,
    ):

        try:
            # =========================
            # 1. Get Emergency Case
            # =========================

            emergency = db.get(
                EmergencyCase,
                emergency_case_id,
            )

            if emergency is None:
                raise ValueError(
                    "Emergency Case not found."
                )

            # =========================
            # 2. AI Triage
            # =========================

            triage = await TriageService.assess(
                db=db,
                emergency_case_id=emergency_case_id,
            )

            # =========================
            # 3. Get Recommendation
            # =========================

            recommendation = RecommendationService.recommend_dispatch(
    db=db,
    emergency_case_id=emergency_case_id,
    recommended_department=triage.recommended_department,
)

            # =========================
            # 4. Get Ambulance
            # =========================

            ambulance = db.get(
                Ambulance,
                recommendation.ambulance_id,
            )

            if ambulance is None:
                raise ValueError(
                    "Recommended ambulance not found."
                )

            # =========================
            # 5. Get Driver
            # =========================

            driver = db.get(
                Driver,
                recommendation.driver_id,
            )

            if driver is None:
                raise ValueError(
                    "Recommended driver not found."
                )

            # =========================
            # 6. Create Incident
            # =========================

            incident = Incident(
                emergency_case_id=emergency.id,
                reported_by=dispatcher_id,
                patient_name=emergency.patient_name,
                patient_age=emergency.patient_age,
                patient_gender=emergency.patient_gender,
                emergency_type=emergency.incident_type.value,
                description=emergency.description,
                latitude=emergency.latitude,
                longitude=emergency.longitude,
                address=emergency.address,

                # Use AI-assessed priority
                severity=triage.recommended_priority,

                # Keep existing deterministic
                # recommendation score
                priority_score=recommendation.priority_score,

                status=EmergencyStatus.DISPATCHED.value,
            )

            db.add(incident)

            # Get incident.id before creating Dispatch
            db.flush()

            # =========================
            # 7. Create Dispatch
            # =========================

            dispatch = Dispatch(
                incident_id=incident.id,
                dispatcher_id=dispatcher_id,
                status=DispatchStatus.CREATED,
            )

            db.add(dispatch)

            # Get dispatch.id
            db.flush()

            # =========================
            # 8. Create Assignment
            # =========================

            assignment = DispatchAssignment(
                dispatch_id=dispatch.id,
                ambulance_id=ambulance.id,
                driver_id=driver.id,
                hospital_id=recommendation.hospital_id,
                status=DispatchAssignmentStatus.ASSIGNED,
            )

            db.add(assignment)

            # =========================
            # 9. Update Ambulance
            # =========================

            ambulance.status = AmbulanceStatus.DISPATCHED

            # =========================
            # 10. Update Driver
            # =========================

            driver.is_available = False

            # =========================
            # 11. Update Emergency
            # =========================

            emergency.status = EmergencyStatus.DISPATCHED

            # =========================
            # 12. Commit Transaction
            # =========================

            db.commit()

            db.refresh(dispatch)

            return dispatch

        except Exception:
            db.rollback()
            raise
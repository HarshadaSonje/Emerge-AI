import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ambulance import (
    Ambulance,
    AmbulanceStatus,
)
from app.models.department import Department
from app.models.driver import Driver
from app.models.emergency_case import EmergencyCase
from app.models.hospital import Hospital

from app.schemas.recommendation import (
    DispatchRecommendationResponse,
)

from app.utils.hospital_matching import (
    required_department,
)
from app.utils.location import calculate_distance
from app.utils.scoring import calculate_priority_score
from app.exceptions.ambulance import (
    NoAvailableAmbulanceException,
    NoAvailableAmbulanceWithDriverException,
)


class RecommendationService:

    @staticmethod
    def find_best_hospital(
        db: Session,
        emergency: EmergencyCase,
        recommended_department: str | None = None,
    ) -> Hospital | None:

        # ---------------------------------
        # Determine required department
        # ---------------------------------
        department_name = (
            recommended_department
            if recommended_department
            else required_department(
                emergency.incident_type,
            )
        )

        hospitals = list(
            db.scalars(
                select(Hospital)
                .join(Department)
                .where(
                    Hospital.is_active.is_(True),
                    Department.name == department_name,
                    Department.is_active.is_(True),
                )
            ).all()
        )

        if hospitals:
            return hospitals[0]

        return None

    @staticmethod
    def recommend_dispatch(
        db: Session,
        emergency_case_id: uuid.UUID,
        recommended_department: str | None = None,
    ) -> DispatchRecommendationResponse:

        # ---------------------------------
        # 1. Get Emergency Case
        # ---------------------------------

        emergency = db.get(
            EmergencyCase,
            emergency_case_id,
        )

        if emergency is None:
            raise ValueError(
                "Emergency Case not found."
            )

        # ---------------------------------
        # 2. Get Available Ambulances
        # ---------------------------------

        ambulances = list(
            db.scalars(
                select(Ambulance).where(
                    Ambulance.status == AmbulanceStatus.AVAILABLE,
                    Ambulance.is_active.is_(True),
                )
            ).all()
        )

        if not ambulances:
         raise NoAvailableAmbulanceException()

        # ---------------------------------
        # 3. Calculate Ambulance Distances
        # ---------------------------------

        ambulance_distances = []

        for ambulance in ambulances:

            distance = calculate_distance(
                emergency.latitude,
                emergency.longitude,
                ambulance.current_latitude,
                ambulance.current_longitude,
            )

            ambulance_distances.append(
                (
                    ambulance,
                    distance,
                )
            )

        # Nearest ambulances first
        ambulance_distances.sort(
            key=lambda x: x[1]
        )

        # ---------------------------------
        # 4. Select Best Ambulance + Driver
        # ---------------------------------

        best_score = -1.0

        selected_ambulance = None
        selected_driver = None
        selected_distance = None

        for ambulance, distance in ambulance_distances:

            driver = db.scalar(
                select(Driver).where(
                    Driver.ambulance_id == ambulance.id,
                    Driver.is_available.is_(True),
                    Driver.is_active.is_(True),
                )
            )

            if driver is None:
                continue

            # Existing deterministic dispatch scoring
            score = calculate_priority_score(
                ambulance=ambulance,
                driver=driver,
                emergency=emergency,
                distance=distance,
            )

            if score > best_score:
                best_score = score
                selected_ambulance = ambulance
                selected_driver = driver
                selected_distance = distance

        if selected_ambulance is None:
            raise NoAvailableAmbulanceWithDriverException()

        # ---------------------------------
        # 5. Find Appropriate Hospital
        # ---------------------------------
        #
        # AI-recommended department is used when
        # available. Otherwise, existing incident
        # type → department mapping is used.
        #

        hospital = RecommendationService.find_best_hospital(
            db=db,
            emergency=emergency,
            recommended_department=recommended_department,
        )

        # ---------------------------------
        # 6. Hospital Fallback
        # ---------------------------------

        hospital_id = (
            hospital.id
            if hospital is not None
            else selected_ambulance.hospital_id
        )

        # ---------------------------------
        # 7. Return Recommendation
        # ---------------------------------

        return DispatchRecommendationResponse(
            ambulance_id=selected_ambulance.id,
            driver_id=selected_driver.id,
            hospital_id=hospital_id,
            distance_km=selected_distance,
            priority_score=best_score,
        )
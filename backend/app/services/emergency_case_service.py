import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.city import CityNotFoundException
from app.exceptions.emergency_case import (
    CaseNumberExistsException,
    EmergencyCaseNotFoundException,
)
from app.models.city import City
from app.models.emergency_case import (
    EmergencyCase,
    EmergencyStatus,
)
from app.schemas.emergency_case import (
    EmergencyCaseCreate,
    EmergencyCaseUpdate,
    EmergencySeverityUpdate,
    EmergencyStatusUpdate,
)


class EmergencyCaseService:

    @staticmethod
    def create_emergency_case(
        db: Session,
        emergency_data: EmergencyCaseCreate,
    ) -> EmergencyCase:

        city = db.get(City, emergency_data.city_id)

        if city is None:
            raise CityNotFoundException()

        case_number = (
            f"EC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        )

        existing_case = db.scalar(
            select(EmergencyCase).where(
                EmergencyCase.case_number == case_number
            )
        )

        if existing_case:
            raise CaseNumberExistsException()

        emergency = EmergencyCase(
            case_number=case_number,
            reporter_name=emergency_data.reporter_name,
            reporter_phone=emergency_data.reporter_phone,
            patient_name=emergency_data.patient_name,
            patient_age=emergency_data.patient_age,
            patient_gender=emergency_data.patient_gender,
            incident_type=emergency_data.incident_type,
            description=emergency_data.description,
            latitude=emergency_data.latitude,
            longitude=emergency_data.longitude,
            address=emergency_data.address,
            city_id=emergency_data.city_id,
        )

        db.add(emergency)
        db.commit()
        db.refresh(emergency)

        return emergency

    @staticmethod
    def get_all_emergency_cases(
        db: Session,
        page: int = 1,
        limit: int = 10,
        status: EmergencyStatus | None = None,
        city_id: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> list[EmergencyCase]:

        query = select(EmergencyCase)

        if status is not None:
            query = query.where(
                EmergencyCase.status == status
            )

        if city_id is not None:
            query = query.where(
                EmergencyCase.city_id == city_id
            )

        if is_active is not None:
            query = query.where(
                EmergencyCase.is_active == is_active
            )

        query = (
            query.order_by(EmergencyCase.reported_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(
            db.scalars(query).all()
        )

    @staticmethod
    def get_emergency_case_by_id(
        db: Session,
        emergency_case_id: uuid.UUID,
    ) -> EmergencyCase:

        emergency = db.get(
            EmergencyCase,
            emergency_case_id,
        )

        if emergency is None:
            raise EmergencyCaseNotFoundException()

        return emergency

    @staticmethod
    def update_emergency_case(
        db: Session,
        emergency_case_id: uuid.UUID,
        emergency_data: EmergencyCaseUpdate,
    ) -> EmergencyCase:

        emergency = db.get(
            EmergencyCase,
            emergency_case_id,
        )

        if emergency is None:
            raise EmergencyCaseNotFoundException()

        if emergency_data.city_id is not None:

            city = db.get(
                City,
                emergency_data.city_id,
            )

            if city is None:
                raise CityNotFoundException()

            emergency.city_id = emergency_data.city_id

        for field, value in emergency_data.model_dump(
            exclude_unset=True,
            exclude={"city_id"},
        ).items():

            setattr(
                emergency,
                field,
                value,
            )

        db.commit()
        db.refresh(emergency)

        return emergency

    @staticmethod
    def update_status(
        db: Session,
        emergency_case_id: uuid.UUID,
        status_data: EmergencyStatusUpdate,
    ) -> EmergencyCase:

        emergency = db.get(
            EmergencyCase,
            emergency_case_id,
        )

        if emergency is None:
            raise EmergencyCaseNotFoundException()

        emergency.status = status_data.status

        db.commit()
        db.refresh(emergency)

        return emergency

    @staticmethod
    def update_severity(
        db: Session,
        emergency_case_id: uuid.UUID,
        severity_data: EmergencySeverityUpdate,
    ) -> EmergencyCase:

        emergency = db.get(
            EmergencyCase,
            emergency_case_id,
        )

        if emergency is None:
            raise EmergencyCaseNotFoundException()

        emergency.severity = severity_data.severity

        db.commit()
        db.refresh(emergency)

        return emergency

    @staticmethod
    def close_emergency_case(
        db: Session,
        emergency_case_id: uuid.UUID,
    ) -> EmergencyCase:

        emergency = db.get(
            EmergencyCase,
            emergency_case_id,
        )

        if emergency is None:
            raise EmergencyCaseNotFoundException()

        emergency.status = EmergencyStatus.COMPLETED
        emergency.closed_at = datetime.utcnow()
        emergency.is_active = False

        db.commit()
        db.refresh(emergency)

        return emergency
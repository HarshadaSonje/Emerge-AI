import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.ambulance import (
    AmbulanceNotFoundException,
    RegistrationNumberExistsException,
    VehicleNumberExistsException,
)
from app.exceptions.ems_organization import (
    EMSOrganizationNotFoundException,
)
from app.exceptions.hospital import (
    HospitalNotFoundException,
)
from app.models.ambulance import (
    Ambulance,
    AmbulanceStatus,
)
from app.models.ems_organization import EMSOrganization
from app.models.hospital import Hospital
from app.schemas.ambulance import (
    AmbulanceCreate,
    AmbulanceLocationUpdate,
    AmbulanceStatusUpdate,
    AmbulanceUpdate,
)


class AmbulanceService:

    @staticmethod
    def create_ambulance(
        db: Session,
        ambulance_data: AmbulanceCreate,
    ) -> Ambulance:
        """
        Create a new ambulance.
        """

        hospital = db.get(
            Hospital,
            ambulance_data.hospital_id,
        )

        if hospital is None:
            raise HospitalNotFoundException()

        ems_organization = db.get(
            EMSOrganization,
            ambulance_data.ems_organization_id,
        )

        if ems_organization is None:
            raise EMSOrganizationNotFoundException()

        if (
            hospital.ems_organization_id
            != ambulance_data.ems_organization_id
        ):
            raise ValueError(
                "Hospital does not belong to the selected EMS Organization."
            )

        registration = db.scalar(
            select(Ambulance).where(
                Ambulance.registration_number
                == ambulance_data.registration_number
            )
        )

        if registration:
            raise RegistrationNumberExistsException()

        vehicle = db.scalar(
            select(Ambulance).where(
                Ambulance.vehicle_number
                == ambulance_data.vehicle_number
            )
        )

        if vehicle:
            raise VehicleNumberExistsException()

        ambulance = Ambulance(
            registration_number=ambulance_data.registration_number,
            vehicle_number=ambulance_data.vehicle_number,
            vehicle_type=ambulance_data.vehicle_type,
            hospital_id=ambulance_data.hospital_id,
            ems_organization_id=ambulance_data.ems_organization_id,
            current_latitude=ambulance_data.current_latitude,
            current_longitude=ambulance_data.current_longitude,
        )

        db.add(ambulance)
        db.commit()
        db.refresh(ambulance)

        return ambulance

    @staticmethod
    def get_all_ambulances(
        db: Session,
        page: int = 1,
        limit: int = 10,
        status: AmbulanceStatus | None = None,
    ) -> list[Ambulance]:

        query = select(Ambulance)

        if status is not None:
            query = query.where(
                Ambulance.status == status
            )

        query = (
            query.order_by(Ambulance.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(
            db.scalars(query).all()
        )

    @staticmethod
    def get_ambulance_by_id(
        db: Session,
        ambulance_id: uuid.UUID,
    ) -> Ambulance:

        ambulance = db.get(
            Ambulance,
            ambulance_id,
        )

        if ambulance is None:
            raise AmbulanceNotFoundException()

        return ambulance

    @staticmethod
    def update_ambulance(
        db: Session,
        ambulance_id: uuid.UUID,
        ambulance_data: AmbulanceUpdate,
    ) -> Ambulance:

        ambulance = db.get(
            Ambulance,
            ambulance_id,
        )

        if ambulance is None:
            raise AmbulanceNotFoundException()

        if (
            ambulance_data.registration_number
            and ambulance_data.registration_number
            != ambulance.registration_number
        ):

            registration = db.scalar(
                select(Ambulance).where(
                    Ambulance.registration_number
                    == ambulance_data.registration_number,
                    Ambulance.id != ambulance_id,
                )
            )

            if registration:
                raise RegistrationNumberExistsException()

            ambulance.registration_number = (
                ambulance_data.registration_number
            )

        if (
            ambulance_data.vehicle_number
            and ambulance_data.vehicle_number
            != ambulance.vehicle_number
        ):

            vehicle = db.scalar(
                select(Ambulance).where(
                    Ambulance.vehicle_number
                    == ambulance_data.vehicle_number,
                    Ambulance.id != ambulance_id,
                )
            )

            if vehicle:
                raise VehicleNumberExistsException()

            ambulance.vehicle_number = (
                ambulance_data.vehicle_number
            )

        if ambulance_data.vehicle_type is not None:
            ambulance.vehicle_type = ambulance_data.vehicle_type

        if ambulance_data.hospital_id is not None:

            hospital = db.get(
                Hospital,
                ambulance_data.hospital_id,
            )

            if hospital is None:
                raise HospitalNotFoundException()

            ambulance.hospital_id = (
                ambulance_data.hospital_id
            )

        if ambulance_data.ems_organization_id is not None:

            organization = db.get(
                EMSOrganization,
                ambulance_data.ems_organization_id,
            )

            if organization is None:
                raise EMSOrganizationNotFoundException()

            ambulance.ems_organization_id = (
                ambulance_data.ems_organization_id
            )

        if ambulance_data.current_latitude is not None:
            ambulance.current_latitude = (
                ambulance_data.current_latitude
            )

        if ambulance_data.current_longitude is not None:
            ambulance.current_longitude = (
                ambulance_data.current_longitude
            )

        db.commit()
        db.refresh(ambulance)

        return ambulance

    @staticmethod
    def activate_ambulance(
        db: Session,
        ambulance_id: uuid.UUID,
    ) -> Ambulance:

        ambulance = db.get(
            Ambulance,
            ambulance_id,
        )

        if ambulance is None:
            raise AmbulanceNotFoundException()

        ambulance.is_active = True

        db.commit()
        db.refresh(ambulance)

        return ambulance

    @staticmethod
    def deactivate_ambulance(
        db: Session,
        ambulance_id: uuid.UUID,
    ) -> Ambulance:

        ambulance = db.get(
            Ambulance,
            ambulance_id,
        )

        if ambulance is None:
            raise AmbulanceNotFoundException()

        ambulance.is_active = False

        db.commit()
        db.refresh(ambulance)

        return ambulance

    @staticmethod
    def update_status(
        db: Session,
        ambulance_id: uuid.UUID,
        status_data: AmbulanceStatusUpdate,
    ) -> Ambulance:

        ambulance = db.get(
            Ambulance,
            ambulance_id,
        )

        if ambulance is None:
            raise AmbulanceNotFoundException()

        ambulance.status = status_data.status

        db.commit()
        db.refresh(ambulance)

        return ambulance

    @staticmethod
    def update_location(
        db: Session,
        ambulance_id: uuid.UUID,
        location_data: AmbulanceLocationUpdate,
    ) -> Ambulance:

        ambulance = db.get(
            Ambulance,
            ambulance_id,
        )

        if ambulance is None:
            raise AmbulanceNotFoundException()

        ambulance.current_latitude = (
            location_data.current_latitude
        )

        ambulance.current_longitude = (
            location_data.current_longitude
        )

        db.commit()
        db.refresh(ambulance)

        return ambulance
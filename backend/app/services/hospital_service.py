from uuid import UUID
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.city import CityNotFoundException
from app.exceptions.ems_organization import EMSOrganizationNotFoundException
from app.exceptions.hospital import (
    HospitalCodeExistsException,
    HospitalEmailExistsException,
    HospitalNotFoundException,
    HospitalPhoneExistsException,
)
from app.models.city import City
from app.models.ems_organization import EMSOrganization
from app.models.hospital import Hospital
from app.schemas.hospital import HospitalCreate, HospitalUpdate


class HospitalService:

    @staticmethod
    def create_hospital(
        db: Session,
        hospital_data: HospitalCreate,
    ) -> Hospital:

        city = db.get(City, hospital_data.city_id)
        if city is None:
            raise CityNotFoundException()

        organization = db.get(
            EMSOrganization,
            hospital_data.ems_organization_id,
        )
        if organization is None:
            raise EMSOrganizationNotFoundException()

        existing_code = db.scalar(
            select(Hospital).where(
                Hospital.code == hospital_data.code
            )
        )

        if existing_code:
            raise HospitalCodeExistsException()

        existing_email = db.scalar(
            select(Hospital).where(
                Hospital.email == hospital_data.email
            )
        )

        if existing_email:
            raise HospitalEmailExistsException()

        existing_phone = db.scalar(
            select(Hospital).where(
                Hospital.phone == hospital_data.phone
            )
        )

        if existing_phone:
            raise HospitalPhoneExistsException()

        hospital = Hospital(
            name=hospital_data.name,
            code=hospital_data.code,
            email=hospital_data.email,
            phone=hospital_data.phone,
            address=hospital_data.address,
            city_id=hospital_data.city_id,
            ems_organization_id=hospital_data.ems_organization_id,
        )

        db.add(hospital)
        db.commit()
        db.refresh(hospital)

        return hospital

    @staticmethod
    def get_all_hospitals(
        db: Session,
        page: int = 1,
        limit: int = 10,
        city_id: uuid.UUID | None = None,
        ems_organization_id: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> list[Hospital]:

        query = select(Hospital)

        if city_id is not None:
            query = query.where(
                Hospital.city_id == city_id
            )

        if ems_organization_id is not None:
            query = query.where(
                Hospital.ems_organization_id == ems_organization_id
            )

        if is_active is not None:
            query = query.where(
                Hospital.is_active == is_active
            )

        query = (
            query.order_by(Hospital.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(
            db.scalars(query).all()
        )

    @staticmethod
    def get_hospital_by_id(
        db: Session,
        hospital_id: UUID,
    ) -> Hospital:

        hospital = db.get(Hospital, hospital_id)

        if hospital is None:
            raise HospitalNotFoundException()

        return hospital

    @staticmethod
    def update_hospital(
        db: Session,
        hospital_id: UUID,
        hospital_data: HospitalUpdate,
    ) -> Hospital:

        hospital = HospitalService.get_hospital_by_id(
            db,
            hospital_id,
        )

        update_data = hospital_data.model_dump(
            exclude_unset=True
        )

        if "city_id" in update_data:
            city = db.get(City, update_data["city_id"])
            if city is None:
                raise CityNotFoundException()

        if "ems_organization_id" in update_data:
            organization = db.get(
                EMSOrganization,
                update_data["ems_organization_id"],
            )
            if organization is None:
                raise EMSOrganizationNotFoundException()

        if "code" in update_data:
            existing = db.scalar(
                select(Hospital).where(
                    Hospital.code == update_data["code"],
                    Hospital.id != hospital_id,
                )
            )

            if existing:
                raise HospitalCodeExistsException()

        if "email" in update_data:
            existing = db.scalar(
                select(Hospital).where(
                    Hospital.email == update_data["email"],
                    Hospital.id != hospital_id,
                )
            )

            if existing:
                raise HospitalEmailExistsException()

        if "phone" in update_data:
            existing = db.scalar(
                select(Hospital).where(
                    Hospital.phone == update_data["phone"],
                    Hospital.id != hospital_id,
                )
            )

            if existing:
                raise HospitalPhoneExistsException()

        for key, value in update_data.items():
            setattr(hospital, key, value)

        db.commit()
        db.refresh(hospital)

        return hospital

    @staticmethod
    def activate_hospital(
        db: Session,
        hospital_id: UUID,
    ) -> Hospital:

        hospital = HospitalService.get_hospital_by_id(
            db,
            hospital_id,
        )

        hospital.is_active = True

        db.commit()
        db.refresh(hospital)

        return hospital

    @staticmethod
    def deactivate_hospital(
        db: Session,
        hospital_id: UUID,
    ) -> Hospital:

        hospital = HospitalService.get_hospital_by_id(
            db,
            hospital_id,
        )

        hospital.is_active = False

        db.commit()
        db.refresh(hospital)

        return hospital
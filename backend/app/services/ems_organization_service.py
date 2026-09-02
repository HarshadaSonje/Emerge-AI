from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.ems_organization import (
    EMSOrganizationCodeExistsException,
    EMSOrganizationEmailExistsException,
    EMSOrganizationNotFoundException,
    EMSOrganizationPhoneExistsException,
)
from app.models.ems_organization import EMSOrganization
from app.schemas.ems_organization import (
    EMSOrganizationCreate,
    EMSOrganizationUpdate,
)


class EMSOrganizationService:

    @staticmethod
    def create_organization(
        db: Session,
        organization_data: EMSOrganizationCreate,
    ) -> EMSOrganization:

        existing_code = db.scalar(
            select(EMSOrganization).where(
                EMSOrganization.code == organization_data.code
            )
        )

        if existing_code:
            raise EMSOrganizationCodeExistsException()

        existing_email = db.scalar(
            select(EMSOrganization).where(
                EMSOrganization.email == organization_data.email
            )
        )

        if existing_email:
            raise EMSOrganizationEmailExistsException()

        existing_phone = db.scalar(
            select(EMSOrganization).where(
                EMSOrganization.phone == organization_data.phone
            )
        )

        if existing_phone:
            raise EMSOrganizationPhoneExistsException()

        organization = EMSOrganization(
            name=organization_data.name,
            code=organization_data.code,
            email=organization_data.email,
            phone=organization_data.phone,
            address=organization_data.address,
            city_id=organization_data.city_id,
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        return organization

    @staticmethod
    def get_all_organizations(
        db: Session,
    ) -> list[EMSOrganization]:

        return list(
            db.scalars(
                select(EMSOrganization).order_by(
                    EMSOrganization.name
                )
            ).all()
        )

    @staticmethod
    def get_organization_by_id(
        db: Session,
        organization_id: UUID,
    ) -> EMSOrganization:

        organization = db.get(
            EMSOrganization,
            organization_id,
        )

        if organization is None:
            raise EMSOrganizationNotFoundException()

        return organization

    @staticmethod
    def update_organization(
        db: Session,
        organization_id: UUID,
        organization_data: EMSOrganizationUpdate,
    ) -> EMSOrganization:

        organization = EMSOrganizationService.get_organization_by_id(
            db,
            organization_id,
        )

        update_data = organization_data.model_dump(
            exclude_unset=True
        )

        if "code" in update_data:
            existing = db.scalar(
                select(EMSOrganization).where(
                    EMSOrganization.code == update_data["code"],
                    EMSOrganization.id != organization_id,
                )
            )

            if existing:
                raise EMSOrganizationCodeExistsException()

        if "email" in update_data:
            existing = db.scalar(
                select(EMSOrganization).where(
                    EMSOrganization.email == update_data["email"],
                    EMSOrganization.id != organization_id,
                )
            )

            if existing:
                raise EMSOrganizationEmailExistsException()

        if "phone" in update_data:
            existing = db.scalar(
                select(EMSOrganization).where(
                    EMSOrganization.phone == update_data["phone"],
                    EMSOrganization.id != organization_id,
                )
            )

            if existing:
                raise EMSOrganizationPhoneExistsException()

        for key, value in update_data.items():
            setattr(organization, key, value)

        db.commit()
        db.refresh(organization)

        return organization

    @staticmethod
    def activate_organization(
        db: Session,
        organization_id: UUID,
    ) -> EMSOrganization:

        organization = EMSOrganizationService.get_organization_by_id(
            db,
            organization_id,
        )

        organization.is_active = True

        db.commit()
        db.refresh(organization)

        return organization

    @staticmethod
    def deactivate_organization(
        db: Session,
        organization_id: UUID,
    ) -> EMSOrganization:

        organization = EMSOrganizationService.get_organization_by_id(
            db,
            organization_id,
        )

        organization.is_active = False

        db.commit()
        db.refresh(organization)

        return organization
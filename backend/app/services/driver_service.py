import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.ambulance import (
    AmbulanceNotFoundException,
)
from app.exceptions.driver import (
    AmbulanceAlreadyAssignedException,
    DriverAlreadyExistsException,
    DriverNotFoundException,
    InvalidLicenseException,
    LicenseNumberExistsException,
)
from app.exceptions.user import (
    UserNotFoundException,
)
from app.models.ambulance import Ambulance
from app.models.driver import Driver
from app.models.user import User
from app.schemas.driver import (
    DriverAmbulanceAssignment,
    DriverAvailabilityUpdate,
    DriverCreate,
    DriverUpdate,
)


class DriverService:

    @staticmethod
    def create_driver(
        db: Session,
        driver_data: DriverCreate,
    ) -> Driver:

        user = db.get(User, driver_data.user_id)

        if user is None:
            raise UserNotFoundException()

        existing_driver = db.scalar(
            select(Driver).where(
                Driver.user_id == driver_data.user_id
            )
        )

        if existing_driver:
            raise DriverAlreadyExistsException()

        existing_license = db.scalar(
            select(Driver).where(
                Driver.license_number
                == driver_data.license_number
            )
        )

        if existing_license:
            raise LicenseNumberExistsException()

        if driver_data.license_expiry < date.today():
            raise InvalidLicenseException()

        if driver_data.ambulance_id:

            ambulance = db.get(
                Ambulance,
                driver_data.ambulance_id,
            )

            if ambulance is None:
                raise AmbulanceNotFoundException()

            assigned = db.scalar(
                select(Driver).where(
                    Driver.ambulance_id
                    == driver_data.ambulance_id
                )
            )

            if assigned:
                raise AmbulanceAlreadyAssignedException()

        driver = Driver(
            user_id=driver_data.user_id,
            ambulance_id=driver_data.ambulance_id,
            license_number=driver_data.license_number,
            license_expiry=driver_data.license_expiry,
            years_of_experience=driver_data.years_of_experience,
        )

        db.add(driver)
        db.commit()
        db.refresh(driver)

        return driver

    @staticmethod
    def get_all_drivers(
        db: Session,
        page: int = 1,
        limit: int = 10,
        is_available: bool | None = None,
        is_active: bool | None = None,
    ) -> list[Driver]:

        query = select(Driver)

        if is_available is not None:
            query = query.where(
                Driver.is_available == is_available
            )

        if is_active is not None:
            query = query.where(
                Driver.is_active == is_active
            )

        query = (
            query.order_by(Driver.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(
            db.scalars(query).all()
        )

    @staticmethod
    def get_driver_by_id(
        db: Session,
        driver_id: uuid.UUID,
    ) -> Driver:

        driver = db.get(
            Driver,
            driver_id,
        )

        if driver is None:
            raise DriverNotFoundException()

        return driver

    @staticmethod
    def update_driver(
        db: Session,
        driver_id: uuid.UUID,
        driver_data: DriverUpdate,
    ) -> Driver:

        driver = db.get(
            Driver,
            driver_id,
        )

        if driver is None:
            raise DriverNotFoundException()

        if (
            driver_data.license_number
            and driver_data.license_number
            != driver.license_number
        ):

            existing_license = db.scalar(
                select(Driver).where(
                    Driver.license_number
                    == driver_data.license_number,
                    Driver.id != driver_id,
                )
            )

            if existing_license:
                raise LicenseNumberExistsException()

            driver.license_number = (
                driver_data.license_number
            )

        if driver_data.license_expiry:

            if driver_data.license_expiry < date.today():
                raise InvalidLicenseException()

            driver.license_expiry = (
                driver_data.license_expiry
            )

        if (
            driver_data.years_of_experience
            is not None
        ):
            driver.years_of_experience = (
                driver_data.years_of_experience
            )

        if driver_data.ambulance_id is not None:

            ambulance = db.get(
                Ambulance,
                driver_data.ambulance_id,
            )

            if ambulance is None:
                raise AmbulanceNotFoundException()

            assigned = db.scalar(
                select(Driver).where(
                    Driver.ambulance_id
                    == driver_data.ambulance_id,
                    Driver.id != driver_id,
                )
            )

            if assigned:
                raise AmbulanceAlreadyAssignedException()

            driver.ambulance_id = (
                driver_data.ambulance_id
            )

        db.commit()
        db.refresh(driver)

        return driver

    @staticmethod
    def activate_driver(
        db: Session,
        driver_id: uuid.UUID,
    ) -> Driver:

        driver = db.get(
            Driver,
            driver_id,
        )

        if driver is None:
            raise DriverNotFoundException()

        driver.is_active = True

        db.commit()
        db.refresh(driver)

        return driver

    @staticmethod
    def deactivate_driver(
        db: Session,
        driver_id: uuid.UUID,
    ) -> Driver:

        driver = db.get(
            Driver,
            driver_id,
        )

        if driver is None:
            raise DriverNotFoundException()

        driver.is_active = False

        db.commit()
        db.refresh(driver)

        return driver

    @staticmethod
    def update_availability(
        db: Session,
        driver_id: uuid.UUID,
        availability_data: DriverAvailabilityUpdate,
    ) -> Driver:

        driver = db.get(
            Driver,
            driver_id,
        )

        if driver is None:
            raise DriverNotFoundException()

        driver.is_available = (
            availability_data.is_available
        )

        db.commit()
        db.refresh(driver)

        return driver

    @staticmethod
    def assign_ambulance(
        db: Session,
        driver_id: uuid.UUID,
        assignment_data: DriverAmbulanceAssignment,
    ) -> Driver:

        driver = db.get(
            Driver,
            driver_id,
        )

        if driver is None:
            raise DriverNotFoundException()

        ambulance = db.get(
            Ambulance,
            assignment_data.ambulance_id,
        )

        if ambulance is None:
            raise AmbulanceNotFoundException()

        assigned = db.scalar(
            select(Driver).where(
                Driver.ambulance_id
                == assignment_data.ambulance_id,
                Driver.id != driver_id,
            )
        )

        if assigned:
            raise AmbulanceAlreadyAssignedException()

        driver.ambulance_id = assignment_data.ambulance_id

        db.commit()
        db.refresh(driver)

        return driver

    @staticmethod
    def remove_ambulance(
        db: Session,
        driver_id: uuid.UUID,
    ) -> Driver:

        driver = db.get(
            Driver,
            driver_id,
        )

        if driver is None:
            raise DriverNotFoundException()

        driver.ambulance_id = None

        db.commit()
        db.refresh(driver)

        return driver
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.city import CityNotFoundException
from app.models.city import City
from app.schemas.city import (
    CityCreate,
    CityUpdate,
)


class CityService:

    @staticmethod
    def create_city(
        db: Session,
        city_data: CityCreate,
    ) -> City:

        city = City(
            name=city_data.name,
            state=city_data.state,
            country=city_data.country,
        )

        db.add(city)
        db.commit()
        db.refresh(city)

        return city

    @staticmethod
    def get_all_cities(
        db: Session,
    ) -> list[City]:

        return list(
            db.scalars(
                select(City)
                .order_by(City.name)
            ).all()
        )

    @staticmethod
    def get_city_by_id(
        db: Session,
        city_id: uuid.UUID,
    ) -> City:

        city = db.get(
            City,
            city_id,
        )

        if city is None:
            raise CityNotFoundException()

        return city

    @staticmethod
    def update_city(
        db: Session,
        city_id: uuid.UUID,
        city_data: CityUpdate,
    ) -> City:

        city = CityService.get_city_by_id(
            db,
            city_id,
        )

        for field, value in city_data.model_dump(
            exclude_unset=True,
        ).items():

            setattr(
                city,
                field,
                value,
            )

        db.commit()
        db.refresh(city)

        return city

    @staticmethod
    def delete_city(
        db: Session,
        city_id: uuid.UUID,
    ) -> None:

        city = CityService.get_city_by_id(
            db,
            city_id,
        )

        db.delete(city)
        db.commit()
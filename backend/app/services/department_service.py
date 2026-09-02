import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.department import (
    DepartmentCodeExistsException,
    DepartmentNotFoundException,
)
from app.exceptions.hospital import HospitalNotFoundException
from app.models.department import Department
from app.models.hospital import Hospital
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
)


class DepartmentService:

    @staticmethod
    def create_department(
        db: Session,
        department_data: DepartmentCreate,
    ) -> Department:
        """
        Create a new department.
        """

        hospital = db.get(
            Hospital,
            department_data.hospital_id,
        )

        if hospital is None:
            raise HospitalNotFoundException()

        existing_department = db.scalar(
            select(Department).where(
                Department.code == department_data.code
            )
        )

        if existing_department:
            raise DepartmentCodeExistsException()

        department = Department(
            hospital_id=department_data.hospital_id,
            name=department_data.name,
            code=department_data.code,
            description=department_data.description,
            floor_number=department_data.floor_number,
            contact_number=department_data.contact_number,
        )

        db.add(department)
        db.commit()
        db.refresh(department)

        return department

    @staticmethod
    def get_all_departments(
        db: Session,
        page: int = 1,
        limit: int = 10,
        hospital_id: uuid.UUID | None = None,
        is_active: bool | None = None,
    ) -> list[Department]:

        query = select(Department)

        if hospital_id is not None:
            query = query.where(
                Department.hospital_id == hospital_id
            )

        if is_active is not None:
            query = query.where(
                Department.is_active == is_active
            )

        query = (
            query.order_by(Department.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )

        return list(
            db.scalars(query).all()
        )

    @staticmethod
    def get_department_by_id(
        db: Session,
        department_id: uuid.UUID,
    ) -> Department:
        """
        Return department by id.
        """

        department = db.get(
            Department,
            department_id,
        )

        if department is None:
            raise DepartmentNotFoundException()

        return department

    @staticmethod
    def update_department(
        db: Session,
        department_id: uuid.UUID,
        department_data: DepartmentUpdate,
    ) -> Department:
        """
        Update department.
        """

        department = db.get(
            Department,
            department_id,
        )

        if department is None:
            raise DepartmentNotFoundException()

        if (
            department_data.code
            and department_data.code != department.code
        ):
            existing_department = db.scalar(
                select(Department).where(
                    Department.code == department_data.code,
                    Department.id != department_id,
                )
            )

            if existing_department:
                raise DepartmentCodeExistsException()

            department.code = department_data.code

        if department_data.name is not None:
            department.name = department_data.name

        if department_data.description is not None:
            department.description = department_data.description

        if department_data.floor_number is not None:
            department.floor_number = department_data.floor_number

        if department_data.contact_number is not None:
            department.contact_number = department_data.contact_number

        db.commit()
        db.refresh(department)

        return department

    @staticmethod
    def activate_department(
        db: Session,
        department_id: uuid.UUID,
    ) -> Department:
        """
        Activate department.
        """

        department = db.get(
            Department,
            department_id,
        )

        if department is None:
            raise DepartmentNotFoundException()

        department.is_active = True

        db.commit()
        db.refresh(department)

        return department

    @staticmethod
    def deactivate_department(
        db: Session,
        department_id: uuid.UUID,
    ) -> Department:
        """
        Deactivate department.
        """

        department = db.get(
            Department,
            department_id,
        )

        if department is None:
            raise DepartmentNotFoundException()

        department.is_active = False

        db.commit()
        db.refresh(department)

        return department
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.user import (
    EmailAlreadyExistsException,
    UserNotFoundException,
)
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        user_data: UserCreate,
    ) -> User:
        """
        Create a new user.
        """

        existing_user = db.scalar(
            select(User).where(User.email == user_data.email)
        )

        if existing_user:
            raise EmailAlreadyExistsException()

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            phone=user_data.phone,
            password_hash=hash_password(user_data.password),
            role=user_data.role,
            ems_organization_id=user_data.ems_organization_id,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_all_users(
        db: Session,
    ) -> list[User]:
        """
        Get all users.
        """

        return list(
            db.scalars(
                select(User).order_by(User.full_name)
            ).all()
        )

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: UUID,
    ) -> User:
        """
        Get a user by ID.
        """

        user = db.get(User, user_id)

        if user is None:
            raise UserNotFoundException()

        return user

    @staticmethod
    def update_user(
        db: Session,
        user_id: UUID,
        user_data: UserUpdate,
    ) -> User:
        """
        Update user details.
        """

        user = UserService.get_user_by_id(db, user_id)

        update_data = user_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def activate_user(
        db: Session,
        user_id: UUID,
    ) -> User:

        user = UserService.get_user_by_id(db, user_id)

        user.is_active = True

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def deactivate_user(
        db: Session,
        user_id: UUID,
    ) -> User:

        user = UserService.get_user_by_id(db, user_id)

        user.is_active = False

        db.commit()
        db.refresh(user)

        return user
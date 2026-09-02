import uuid

from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.exceptions.auth import (
    InactiveUserException,
    InvalidCredentialsException,
    InvalidTokenException,
)
from app.exceptions.user import UserNotFoundException
from app.models.user import User
from app.schemas.auth import TokenResponse
from app.utils.jwt import create_access_token, decode_access_token
from app.utils.security import verify_password


class AuthService:
    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate a user using email and password.
        """

        user = db.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            raise InvalidCredentialsException()

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InactiveUserException()

        return user

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
    ) -> TokenResponse:
        """
        Login user and return JWT access token.
        """

        user = AuthService.authenticate_user(
            db=db,
            email=email,
            password=password,
        )

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            }
        )

        return TokenResponse(
            access_token=access_token,
        )

    @staticmethod
    def get_current_user(
        db: Session,
        token: str,
    ) -> User:
        """
        Retrieve the currently authenticated user from JWT.
        """

        try:
            payload = decode_access_token(token)

        except JWTError:
            raise InvalidTokenException()

        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidTokenException()

        user = db.get(
            User,
            uuid.UUID(user_id),
        )

        if user is None:
            raise UserNotFoundException()

        if not user.is_active:
            raise InactiveUserException()

        return user
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import Optional

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    CITIZEN = "CITIZEN"
    DISPATCHER = "DISPATCHER"
    DRIVER = "DRIVER"
    HOSPITAL_STAFF = "HOSPITAL_STAFF"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, name="user_role"),
        nullable=False,
    )

    ems_organization_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ems_organizations.id"),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    ems_organization: Mapped["EMSOrganization"] = relationship(
        "EMSOrganization",
    )

    ems_organization: Mapped["EMSOrganization"] = relationship(
        "EMSOrganization",
        back_populates="users",
    )

    driver_profile: Mapped["DriverProfile | None"] = relationship(
        "DriverProfile",
        back_populates="user",
    )
    dispatcher_profile: Mapped["DispatcherProfile | None"] = relationship(
        "DispatcherProfile",
        back_populates="user",
    )
    hospital_staff_profile: Mapped["HospitalStaffProfile | None"] = relationship(
        "HospitalStaffProfile",
        back_populates="user",
    )
    incidents: Mapped[list["Incident"]] = relationship(
        "Incident",
        back_populates="reporter",
    )
    dispatches: Mapped[list["Dispatch"]] = relationship(
        "Dispatch",
        back_populates="dispatcher",
    )
    driver: Mapped[Optional["Driver"]] = relationship(
        "Driver",
        back_populates="user",
        uselist=False,
    )
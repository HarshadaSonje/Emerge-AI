import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EMSOrganization(Base):
    __tablename__ = "ems_organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )

    address: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id"),
        nullable=False,
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

    # Relationships

    city: Mapped["City"] = relationship(
        "City",
        back_populates="ems_organizations",
    )

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="ems_organization",
    )

    ambulances: Mapped[list["Ambulance"]] = relationship(
        "Ambulance",
        back_populates="ems_organization",
    )

    hospitals: Mapped[list["Hospital"]] = relationship(
        "Hospital",
        back_populates="ems_organization",
    )
    ambulances: Mapped[list["Ambulance"]] = relationship(
        "Ambulance",
        back_populates="ems_organization",
    )
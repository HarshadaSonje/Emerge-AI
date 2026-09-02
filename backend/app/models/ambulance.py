import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VehicleType(str, Enum):
    BLS = "BLS"
    ALS = "ALS"
    ICU = "ICU"
    BIKE = "BIKE"


class AmbulanceStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"
    ON_ROUTE = "ON_ROUTE"
    AT_SCENE = "AT_SCENE"
    TRANSPORTING = "TRANSPORTING"
    AT_HOSPITAL = "AT_HOSPITAL"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"


class Ambulance(Base):
    __tablename__ = "ambulances"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    registration_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
    )

    vehicle_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )

    vehicle_type: Mapped[VehicleType] = mapped_column(
        SQLEnum(VehicleType),
        nullable=False,
    )

    status: Mapped[AmbulanceStatus] = mapped_column(
        SQLEnum(AmbulanceStatus),
        default=AmbulanceStatus.AVAILABLE,
        nullable=False,
    )

    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hospitals.id"),
        nullable=False,
    )

    ems_organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ems_organizations.id"),
        nullable=False,
    )

    current_latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    current_longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
        back_populates="ambulances",
    )

    ems_organization: Mapped["EMSOrganization"] = relationship(
        "EMSOrganization",
        back_populates="ambulances",
    )
    drivers: Mapped[list["Driver"]] = relationship(
        "Driver",
        back_populates="ambulance",
    )
    dispatch_assignments: Mapped[list["DispatchAssignment"]] = relationship(
        "DispatchAssignment",
        back_populates="ambulance",
    )
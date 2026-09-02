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
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IncidentType(str, Enum):
    ACCIDENT = "ACCIDENT"
    CARDIAC = "CARDIAC"
    FIRE = "FIRE"
    STROKE = "STROKE"
    TRAUMA = "TRAUMA"
    PREGNANCY = "PREGNANCY"
    POISONING = "POISONING"
    RESPIRATORY = "RESPIRATORY"
    OTHER = "OTHER"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EmergencyStatus(str, Enum):
    REPORTED = "REPORTED"
    VERIFIED = "VERIFIED"
    DISPATCHED = "DISPATCHED"
    AMBULANCE_ARRIVED = "AMBULANCE_ARRIVED"
    PATIENT_PICKED = "PATIENT_PICKED"
    HOSPITAL_ASSIGNED = "HOSPITAL_ASSIGNED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class EmergencyCase(Base):
    __tablename__ = "emergency_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    case_number: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
    )

    reporter_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reporter_phone: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    patient_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    patient_age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    patient_gender: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )

    incident_type: Mapped[IncidentType] = mapped_column(
        SQLEnum(IncidentType),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id"),
        nullable=False,
    )

    severity: Mapped[Severity] = mapped_column(
        SQLEnum(Severity),
        nullable=False,
        default=Severity.MEDIUM,
    )

    status: Mapped[EmergencyStatus] = mapped_column(
        SQLEnum(EmergencyStatus),
        nullable=False,
        default=EmergencyStatus.REPORTED,
    )

    reported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
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

    # =========================
    # Relationships
    # =========================

    city: Mapped["City"] = relationship(
        "City",
        back_populates="emergency_cases",
    )

    incident: Mapped["Incident | None"] = relationship(
        "Incident",
        back_populates="emergency_case",
        uselist=False,
    )
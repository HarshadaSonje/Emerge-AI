from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ambulance import (
    Ambulance,
    AmbulanceStatus,
)
from app.models.department import Department
from app.models.dispatch import (
    Dispatch,
    DispatchStatus,
)
from app.models.driver import Driver
from app.models.emergency_case import (
    EmergencyCase,
    EmergencyStatus,
)
from app.models.hospital import Hospital
from app.schemas.dashboard import (
    AmbulanceStatusSummaryResponse,
    DashboardOverviewResponse,
    EmergencyTrendResponse,
)


class DashboardService:

    @staticmethod
    def get_dashboard_overview(
        db: Session,
    ) -> DashboardOverviewResponse:
        """
        Returns summary statistics for the dashboard.
        """

        # =========================
        # Ambulance Statistics
        # =========================

        total_ambulances = db.scalar(
            select(func.count(Ambulance.id))
            .where(Ambulance.is_active.is_(True))
        ) or 0

        available_ambulances = db.scalar(
            select(func.count(Ambulance.id))
            .where(
                Ambulance.is_active.is_(True),
                Ambulance.status == AmbulanceStatus.AVAILABLE,
            )
        ) or 0

        busy_ambulances = db.scalar(
            select(func.count(Ambulance.id))
            .where(
                Ambulance.is_active.is_(True),
                Ambulance.status.in_(
                    [
                        AmbulanceStatus.DISPATCHED,
                        AmbulanceStatus.ON_ROUTE,
                        AmbulanceStatus.AT_SCENE,
                        AmbulanceStatus.TRANSPORTING,
                        AmbulanceStatus.AT_HOSPITAL,
                    ]
                ),
            )
        ) or 0

        maintenance_ambulances = db.scalar(
            select(func.count(Ambulance.id))
            .where(
                Ambulance.is_active.is_(True),
                Ambulance.status == AmbulanceStatus.MAINTENANCE,
            )
        ) or 0

        # =========================
        # Driver Statistics
        # =========================

        total_drivers = db.scalar(
            select(func.count(Driver.id))
            .where(Driver.is_active.is_(True))
        ) or 0

        available_drivers = db.scalar(
            select(func.count(Driver.id))
            .where(
                Driver.is_active.is_(True),
                Driver.is_available.is_(True),
            )
        ) or 0

        # =========================
        # Hospital Statistics
        # =========================

        total_hospitals = db.scalar(
            select(func.count(Hospital.id))
            .where(Hospital.is_active.is_(True))
        ) or 0

        # =========================
        # Department Statistics
        # =========================

        total_departments = db.scalar(
            select(func.count(Department.id))
            .where(Department.is_active.is_(True))
        ) or 0

        # =========================
        # Emergency Statistics
        # =========================

        active_emergencies = db.scalar(
            select(func.count(EmergencyCase.id))
            .where(
                EmergencyCase.is_active.is_(True),
                EmergencyCase.status.notin_(
                    [
                        EmergencyStatus.COMPLETED,
                        EmergencyStatus.CANCELLED,
                    ]
                ),
            )
        ) or 0

        completed_emergencies = db.scalar(
            select(func.count(EmergencyCase.id))
            .where(
                EmergencyCase.status
                == EmergencyStatus.COMPLETED
            )
        ) or 0

        # =========================
        # Dispatch Statistics
        # =========================

        active_dispatches = db.scalar(
            select(func.count(Dispatch.id))
            .where(
                Dispatch.status.in_(
                    [
                        DispatchStatus.CREATED,
                        DispatchStatus.ACCEPTED,
                        DispatchStatus.EN_ROUTE,
                    ]
                )
            )
        ) or 0

        completed_dispatches = db.scalar(
            select(func.count(Dispatch.id))
            .where(
                Dispatch.status
                == DispatchStatus.COMPLETED
            )
        ) or 0

        # =========================
        # Response
        # =========================

        return DashboardOverviewResponse(
            total_ambulances=total_ambulances,
            available_ambulances=available_ambulances,
            busy_ambulances=busy_ambulances,
            maintenance_ambulances=maintenance_ambulances,
            total_drivers=total_drivers,
            available_drivers=available_drivers,
            total_hospitals=total_hospitals,
            total_departments=total_departments,
            active_emergencies=active_emergencies,
            completed_emergencies=completed_emergencies,
            active_dispatches=active_dispatches,
            completed_dispatches=completed_dispatches,
        )

    @staticmethod
    def get_recent_emergencies(
        db: Session,
        limit: int = 5,
    ) -> list[EmergencyCase]:

        return list(
            db.scalars(
                select(EmergencyCase)
                .where(
                    EmergencyCase.is_active.is_(True)
                )
                .order_by(
                    EmergencyCase.reported_at.desc()
                )
                .limit(limit)
            ).all()
        )

    @staticmethod
    def get_ambulance_status_summary(
        db: Session,
    ) -> list[AmbulanceStatusSummaryResponse]:

        results = db.execute(
            select(
                Ambulance.status,
                func.count(Ambulance.id),
            )
            .where(
                Ambulance.is_active.is_(True)
            )
            .group_by(
                Ambulance.status,
            )
        ).all()

        return [
            AmbulanceStatusSummaryResponse(
                status=status.value,
                count=count,
            )
            for status, count in results
        ]

    @staticmethod
    def get_emergency_trends(
        db: Session,
    ) -> list[EmergencyTrendResponse]:

        results = db.execute(
            select(
                func.date(EmergencyCase.reported_at),
                func.count(EmergencyCase.id),
            )
            .group_by(
                func.date(EmergencyCase.reported_at),
            )
            .order_by(
                func.date(EmergencyCase.reported_at),
            )
        ).all()

        return [
            EmergencyTrendResponse(
                date=date,
                count=count,
            )
            for date, count in results
        ]
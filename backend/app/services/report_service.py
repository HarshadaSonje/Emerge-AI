from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ambulance import Ambulance
from app.models.dispatch_assignment import DispatchAssignment
from app.models.driver import Driver
from app.models.emergency_case import (
    EmergencyCase,
    EmergencyStatus,
    Severity,
)
from app.models.hospital import Hospital

from app.schemas.report import (
    AmbulanceUtilizationResponse,
    DailyReportResponse,
    DriverPerformanceResponse,
    HospitalWorkloadResponse,
)


class ReportService:

    @staticmethod
    def get_daily_report(
        db: Session,
        report_date: date,
    ) -> DailyReportResponse:

        # =========================
        # Total Cases
        # =========================

        total_cases = db.scalar(
            select(func.count(EmergencyCase.id))
            .where(
                func.date(EmergencyCase.reported_at)
                == report_date,
                EmergencyCase.is_active.is_(True),
            )
        ) or 0

        # =========================
        # Active Cases
        # =========================

        active_cases = db.scalar(
            select(func.count(EmergencyCase.id))
            .where(
                func.date(EmergencyCase.reported_at)
                == report_date,
                EmergencyCase.is_active.is_(True),
                EmergencyCase.status.notin_(
                    [
                        EmergencyStatus.COMPLETED,
                        EmergencyStatus.CANCELLED,
                    ]
                ),
            )
        ) or 0

        # =========================
        # Completed Cases
        # =========================

        completed_cases = db.scalar(
            select(func.count(EmergencyCase.id))
            .where(
                func.date(EmergencyCase.reported_at)
                == report_date,
                EmergencyCase.status
                == EmergencyStatus.COMPLETED,
            )
        ) or 0

        # =========================
        # Critical Cases
        # =========================

        critical_cases = db.scalar(
            select(func.count(EmergencyCase.id))
            .where(
                func.date(EmergencyCase.reported_at)
                == report_date,
                EmergencyCase.is_active.is_(True),
                EmergencyCase.severity
                == Severity.CRITICAL,
            )
        ) or 0

        return DailyReportResponse(
            date=report_date,
            total_cases=total_cases,
            active_cases=active_cases,
            completed_cases=completed_cases,
            critical_cases=critical_cases,
        )

    @staticmethod
    def get_ambulance_utilization(
        db: Session,
    ) -> list[AmbulanceUtilizationResponse]:

        results = db.execute(
            select(
                Ambulance.id,
                Ambulance.registration_number,
                Ambulance.vehicle_number,
                Ambulance.status,
                func.count(
                    DispatchAssignment.id
                ).label("dispatch_count"),
            )
            .outerjoin(
                DispatchAssignment,
                Ambulance.id
                == DispatchAssignment.ambulance_id,
            )
            .where(
                Ambulance.is_active.is_(True)
            )
            .group_by(
                Ambulance.id,
                Ambulance.registration_number,
                Ambulance.vehicle_number,
                Ambulance.status,
            )
            .order_by(
                func.count(
                    DispatchAssignment.id
                ).desc()
            )
        ).all()

        return [
            AmbulanceUtilizationResponse(
                ambulance_id=ambulance_id,
                registration_number=registration_number,
                vehicle_number=vehicle_number,
                status=status.value,
                dispatch_count=dispatch_count,
            )
            for (
                ambulance_id,
                registration_number,
                vehicle_number,
                status,
                dispatch_count,
            ) in results
        ]

    @staticmethod
    def get_driver_performance(
        db: Session,
    ) -> list[DriverPerformanceResponse]:

        results = db.execute(
            select(
                Driver.id,
                Driver.license_number,
                Driver.years_of_experience,
                Driver.is_available,
                func.count(
                    DispatchAssignment.id
                ).label("dispatch_count"),
            )
            .outerjoin(
                DispatchAssignment,
                Driver.id
                == DispatchAssignment.driver_id,
            )
            .where(
                Driver.is_active.is_(True)
            )
            .group_by(
                Driver.id,
                Driver.license_number,
                Driver.years_of_experience,
                Driver.is_available,
            )
            .order_by(
                func.count(
                    DispatchAssignment.id
                ).desc()
            )
        ).all()

        return [
            DriverPerformanceResponse(
                driver_id=driver_id,
                license_number=license_number,
                years_of_experience=years_of_experience,
                is_available=is_available,
                dispatch_count=dispatch_count,
            )
            for (
                driver_id,
                license_number,
                years_of_experience,
                is_available,
                dispatch_count,
            ) in results
        ]

    @staticmethod
    def get_hospital_workload(
        db: Session,
    ) -> list[HospitalWorkloadResponse]:

        results = db.execute(
            select(
                Hospital.id,
                Hospital.name,
                func.count(
                    DispatchAssignment.id
                ).label("total_assignments"),
            )
            .outerjoin(
                DispatchAssignment,
                Hospital.id
                == DispatchAssignment.hospital_id,
            )
            .where(
                Hospital.is_active.is_(True)
            )
            .group_by(
                Hospital.id,
                Hospital.name,
            )
            .order_by(
                func.count(
                    DispatchAssignment.id
                ).desc()
            )
        ).all()

        return [
            HospitalWorkloadResponse(
                hospital_id=hospital_id,
                hospital_name=hospital_name,
                total_assignments=total_assignments,
            )
            for (
                hospital_id,
                hospital_name,
                total_assignments,
            ) in results
        ]
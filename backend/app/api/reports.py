from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.report import (
    AmbulanceUtilizationResponse,
    DailyReportResponse,
    DriverPerformanceResponse,
    HospitalWorkloadResponse,
)

from app.services.report_service import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get(
    "/daily",
    response_model=DailyReportResponse,
)
def get_daily_report(
    report_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ReportService.get_daily_report(
        db=db,
        report_date=report_date,
    )


@router.get(
    "/ambulance-utilization",
    response_model=list[AmbulanceUtilizationResponse],
)
def get_ambulance_utilization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ReportService.get_ambulance_utilization(
        db=db,
    )


@router.get(
    "/driver-performance",
    response_model=list[DriverPerformanceResponse],
)
def get_driver_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ReportService.get_driver_performance(
        db=db,
    )


@router.get(
    "/hospital-workload",
    response_model=list[HospitalWorkloadResponse],
)
def get_hospital_workload(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ReportService.get_hospital_workload(
        db=db,
    )
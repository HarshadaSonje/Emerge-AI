from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.users import router as user_router
from app.core.config import settings
from app.db.session import engine
from app.exceptions.handlers import register_exception_handlers
from app.api.ems_organizations import router as ems_organization_router
from app.api.hospitals import router as hospital_router
from app.api.departments import router as department_router
from app.api.ambulances import router as ambulance_router
from app.api.driver import router as driver_router
from app.api.emergency_cases import (
    router as emergency_case_router,
)
from app.api.dispatches import router as dispatch_router
from app.api.dispatch_assignments import (
    router as dispatch_assignment_router,
)
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router
from app.api.recommendation import (
    router as recommendation_router,
)
from app.api.auto_dispatch import (
    router as auto_dispatch_router,
)
from app.api import cities
from app.websocket.routes import router as websocket_router
from app.api.ai_triage import router as ai_triage_router
from app.api.triage import router as triage_router

masked_url = settings.DATABASE_URL.replace(
    settings.POSTGRES_PASSWORD,
    "********",
)

print(masked_url)

app = FastAPI(
    title="EMERGE-AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://emerge-ai.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Exception Handlers
register_exception_handlers(app)

# Register Routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(ems_organization_router)
app.include_router(hospital_router)
app.include_router(department_router)
app.include_router(ambulance_router)
app.include_router(driver_router)
app.include_router(emergency_case_router)
app.include_router(dispatch_router)
app.include_router(dispatch_assignment_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(
    recommendation_router
)
app.include_router(auto_dispatch_router)
app.include_router(cities.router)
app.include_router(websocket_router)
app.include_router(ai_triage_router)
app.include_router(triage_router)

@app.get("/")
def root():
    return {
        "message": "EMERGE-AI Backend Running",
        "database": settings.POSTGRES_DB,
    }


@app.get("/health")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "Database Connected",
    }

from app.models.ambulance import Ambulance
from app.models.driver import Driver
from app.models.emergency_case import EmergencyCase


def calculate_priority_score(
    ambulance: Ambulance,
    driver: Driver,
    emergency: EmergencyCase,
    distance: float,
) -> float:

    score = 0

    # -----------------------
    # Distance
    # -----------------------

    if distance <= 2:
        score += 40
    elif distance <= 5:
        score += 30
    elif distance <= 10:
        score += 20
    else:
        score += 10

    # -----------------------
    # Driver Experience
    # -----------------------

    if driver.years_of_experience >= 10:
        score += 20
    elif driver.years_of_experience >= 5:
        score += 15
    else:
        score += 10

    # -----------------------
    # Ambulance Type
    # -----------------------

    if ambulance.vehicle_type == "ALS":
        score += 25
    else:
        score += 15

    # -----------------------
    # Emergency Severity
    # -----------------------

    severity_scores = {
        "LOW": 5,
        "MEDIUM": 10,
        "HIGH": 15,
        "CRITICAL": 20,
    }

    score += severity_scores[
        emergency.severity.value
    ]

    return score
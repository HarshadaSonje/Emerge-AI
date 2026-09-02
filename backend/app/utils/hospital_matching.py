from app.models.emergency_case import IncidentType


def required_department(
    incident_type: IncidentType,
) -> str:

    mapping = {
        IncidentType.CARDIAC: "Cardiology",
        IncidentType.STROKE: "Neurology",
        IncidentType.TRAUMA: "Trauma",
        IncidentType.PREGNANCY: "Gynecology",
        IncidentType.RESPIRATORY: "Pulmonology",
        IncidentType.FIRE: "Burn Unit",
        IncidentType.ACCIDENT: "Emergency",
        IncidentType.POISONING: "Emergency",
        IncidentType.OTHER: "Emergency",
    }

    return mapping.get(
        incident_type,
        "Emergency",
    )
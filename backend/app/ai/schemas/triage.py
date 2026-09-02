from typing import Literal

from pydantic import BaseModel, Field


class TriageAssessment(BaseModel):
    urgency: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    ] = Field(
        description="AI-assessed urgency of the emergency."
    )

    recommended_priority: int = Field(
        ge=1,
        le=4,
        description=(
            "Recommended priority from 1 (lowest) "
            "to 4 (highest)."
        ),
    )

    recommended_department: str = Field(
        description=(
            "Hospital department most appropriate "
            "for the emergency."
        ),
    )

    reasoning: str = Field(
        description=(
            "Brief explanation of the clinical factors "
            "that influenced the assessment."
        ),
    )

    immediate_attention: bool = Field(
        description=(
            "Whether the case appears to require "
            "immediate medical attention."
        ),
    )
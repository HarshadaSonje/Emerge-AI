import asyncio
import uuid

from google.adk.runners import InMemoryRunner
from google.genai import types
from sqlalchemy.orm import Session

from app.ai.agents.triage_agent import triage_agent
from app.ai.schemas.triage import TriageAssessment
from app.models.emergency_case import EmergencyCase


class TriageService:

    @staticmethod
    async def assess(
        db: Session,
        emergency_case_id: uuid.UUID,
    ) -> TriageAssessment:

        emergency = db.get(
            EmergencyCase,
            emergency_case_id,
        )

        if emergency is None:
            raise ValueError(
                "Emergency Case not found."
            )

        prompt = f"""
Analyze this emergency case.

Patient information:
- Name: {emergency.patient_name or "Not provided"}
- Age: {emergency.patient_age or "Not provided"}
- Gender: {emergency.patient_gender or "Not provided"}

Emergency information:
- Incident type: {emergency.incident_type.value}
- Description: {emergency.description}
- Existing severity: {emergency.severity.value}
- Location: {emergency.address}

Provide the structured triage assessment.
"""

        runner = InMemoryRunner(
            agent=triage_agent,
            app_name="emerge_ai",
        )

        user_id = "emerge_ai_system"
        session_id = str(uuid.uuid4())

        await runner.session_service.create_session(
            app_name="emerge_ai",
            user_id=user_id,
            session_id=session_id,
        )

        content = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=prompt,
                )
            ],
        )

        final_response = None

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response():
                final_response = event

        if final_response is None:
            raise RuntimeError(
                "Triage Agent did not return a response."
            )

        if not final_response.content:
            raise RuntimeError(
                "Triage Agent returned empty content."
            )

        text = final_response.content.parts[0].text

        return TriageAssessment.model_validate_json(
            text
        )
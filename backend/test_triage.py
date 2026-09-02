import asyncio
import uuid

from dotenv import load_dotenv

load_dotenv()

from app.db.session import SessionLocal
from app.ai.services.triage_service import TriageService


async def main():
    db = SessionLocal()

    try:
        # Replace this with an actual emergency_case_id
        emergency_case_id = uuid.UUID(
            "47762c35-f26b-4a07-af93-f1960bda08c6"
        )

        result = await TriageService.assess(
            db=db,
            emergency_case_id=emergency_case_id,
        )

        print("\n===== AI TRIAGE RESULT =====")
        print(result.model_dump_json(indent=2))

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
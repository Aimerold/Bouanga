from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.deps import get_current_admin
from app.models import Admin, ProjectSubmission
from app.schemas import SubmissionCreate, SubmissionOut
from app.services.telegram import send_telegram_message

router = APIRouter(tags=["submissions"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/contact", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_submission(
    payload: SubmissionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    submission = ProjectSubmission(
        type=payload.type,
        project_id=payload.project_id,
        project_title=payload.project_title,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        reason=payload.reason,
        ip_address=request.client.host if request.client else None,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    message = f"""
🆕 New Customer

👤 Customer Info:

Full name: {payload.first_name or "N/A"} {payload.last_name or "N/A"}
Email: {payload.email or "N/A"}
Project: {payload.project_title or "N/A"}
Reason: {payload.reason or "N/A"}

Aimerold Bouanga Resume.
""".strip()

    try:
        await send_telegram_message(message)
    except Exception as e:
        print(f"Telegram error: {e}")

    return submission

from typing import List
from app.services.telegram import send_telegram_message
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.deps import get_current_admin
from app.models import Admin, ProjectSubmission
from app.schemas import SubmissionCreate, SubmissionOut

router = APIRouter(tags=["submissions"])

# Limiteur de débit anti-spam, partagé avec main.py
limiter = Limiter(key_func=get_remote_address)


# ---------- Endpoint PUBLIC : appelé par le formulaire React (Join/Buy/Contact) ----------

@router.post("/contact", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # évite le spam/bot sur un endpoint public sans auth
async def create_submission(
    payload: SubmissionCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Reçoit les données du Modal (firstName, lastName, email, reason) envoyées
    quand un visiteur clique 'Join Project' ou 'Buy Project' sur le portfolio.
    """
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
    
    await send_telegram_message(
        
    f"""
    🆕 New Customer

    👤 Customer Info:

    Full name: {payload.first_name or "N/A"} {payload.last_name or "N/A"}
    
    Email: {payload.email or "N/A"}
    
    Project: {payload.project_title or "N/A"}
    
    Reason: {payload.reason or "N/A"}
    
    Aimerold Bouanga Resume.
    """).strip()
     
    return submission
    
#from textwrap import dedent

#message = dedent



# ---------- Endpoints PROTÉGÉS (JWT requis) : back-office pour toi seul ----------

@router.get("/admin/submissions", response_model=List[SubmissionOut])
def list_submissions(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return (
        db.query(ProjectSubmission)
        .order_by(ProjectSubmission.created_at.desc())
        .all()
    )


@router.get("/admin/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    submission = db.query(ProjectSubmission).filter(ProjectSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demande introuvable")
    submission.is_read = True
    db.commit()
    db.refresh(submission)
    return submission


@router.delete("/admin/submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    submission = db.query(ProjectSubmission).filter(ProjectSubmission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demande introuvable")
    db.delete(submission)
    db.commit()
    return None
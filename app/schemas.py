from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models import SubmissionType


# ---------- Auth ----------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class AdminOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# ---------- Project Submissions (formulaires Join/Buy/Contact) ----------

class SubmissionCreate(BaseModel):
    type: SubmissionType = SubmissionType.contact
    project_id: Optional[str] = None
    project_title: Optional[str] = None
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    reason: str = Field(min_length=1, max_length=2000)


class SubmissionOut(BaseModel):
    id: int
    type: SubmissionType
    project_id: Optional[str]
    project_title: Optional[str]
    first_name: str
    last_name: str
    email: EmailStr
    reason: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
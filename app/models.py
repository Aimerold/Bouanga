import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class SubmissionType(str, enum.Enum):
    join = "join"        # bouton "Join Project"
    buy = "buy"           # bouton "Buy Project"
    contact = "contact"   # formulaire de contact générique (optionnel, footer)


class Admin(Base):
    """Compte administrateur unique (toi) — pas d'inscription publique."""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ProjectSubmission(Base):
    """
    Une demande envoyée depuis le portfolio (Join Project / Buy Project / Contact).
    Remplace le console.log actuel par un vrai enregistrement persistant.
    """
    __tablename__ = "project_submissions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(SubmissionType), nullable=False, default=SubmissionType.contact)
    project_id = Column(String, nullable=True)      # ex: "classhub"
    project_title = Column(String, nullable=True)   # ex: "ClassHub"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    reason = Column(Text, nullable=False)

    ip_address = Column(String, nullable=True)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
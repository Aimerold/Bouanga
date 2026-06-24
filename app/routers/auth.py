from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_admin
from app.models import Admin
from app.schemas import AdminOut, Token
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Connexion admin. form_data.username = email (convention OAuth2 standard).
    Renvoie un JWT à utiliser en header : Authorization: Bearer <token>
    """
    admin = db.query(Admin).filter(Admin.email == form_data.username).first()

    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte désactivé")

    access_token = create_access_token(
        subject=admin.email,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=access_token)


@router.get("/me", response_model=AdminOut)
def read_current_admin(current_admin: Admin = Depends(get_current_admin)):
    """Endpoint protégé de test : confirme que le JWT envoyé est valide."""
    return current_admin
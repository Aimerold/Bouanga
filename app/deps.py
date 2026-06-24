from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Admin
from app.security import decode_access_token

# tokenUrl pointe vers l'endpoint de login (utilisé par /docs pour le bouton "Authorize")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou expirés",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    admin = db.query(Admin).filter(Admin.email == email).first()
    if admin is None or not admin.is_active:
        raise credentials_exception

    return admin
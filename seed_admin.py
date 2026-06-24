"""
Crée (ou met à jour) le compte administrateur unique du portfolio.

Usage :
    python seed_admin.py

Lit ADMIN_EMAIL et ADMIN_PASSWORD depuis .env, ou les demande en interactif
si non définis. Il n'y a volontairement AUCUNE route d'inscription publique
dans l'API : ce script est la seule façon de créer/modifier l'admin.
"""
import getpass

from app.database import Base, SessionLocal, engine
from app.config import settings
from app.models import Admin
from app.security import hash_password


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    email = settings.ADMIN_EMAIL or input("Email admin: ").strip()
    password = settings.ADMIN_PASSWORD or getpass.getpass("Mot de passe admin: ")

    if not email or not password:
        print("Email et mot de passe sont requis.")
        return

    existing = db.query(Admin).filter(Admin.email == email).first()
    if existing:
        existing.hashed_password = hash_password(password)
        db.commit()
        print(f"Mot de passe mis à jour pour {email}.")
    else:
        admin = Admin(
            email=email,
            hashed_password=hash_password(password),
            full_name="BOUANGA MAKITA Aime Rold",
        )
        db.add(admin)
        db.commit()
        print(f"Compte admin créé pour {email}.")

    db.close()


if __name__ == "__main__":
    main()
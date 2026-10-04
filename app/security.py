import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Utilisateur import Utilisateur


password_manager = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

if not SECRET_KEY:
    raise RuntimeError(
        "La variable JWT_SECRET_KEY est absente du fichier .env"
    )


def hash_password(password: str) -> str:
    return password_manager.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str | None,
) -> bool:
    if not hashed_password:
        return False

    return password_manager.verify(
        plain_password,
        hashed_password,
    )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> Utilisateur | None:
    utilisateur = db.scalar(
        select(Utilisateur).where(
            Utilisateur.email == email.lower()
        )
    )

    if utilisateur is None:
        return None

    if not verify_password(
        password,
        utilisateur.password_hash,
    ):
        return None

    return utilisateur


def create_access_token(
    subject: str,
    expires_minutes: int | None = None,
) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(
        minutes=(
            expires_minutes
            if expires_minutes is not None
            else ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": subject,
        "exp": expiration,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
) -> Utilisateur:
    exception_unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if subject is None:
            raise exception_unauthorized

        user_id = int(subject)

    except (InvalidTokenError, ValueError):
        raise exception_unauthorized

    utilisateur = db.get(Utilisateur, user_id)

    if utilisateur is None:
        raise exception_unauthorized

    if not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé",
        )

    return utilisateur

def require_admin(
    current_user: Annotated[Utilisateur, Depends(get_current_user)],
) -> Utilisateur:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs",
        )

    return current_user
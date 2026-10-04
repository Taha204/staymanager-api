from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import Token
from app.security import (
    authenticate_user,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentification"],
)


@router.post(
    "/token",
    response_model=Token,
)
def connexion(
    formulaire: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    utilisateur = authenticate_user(
        db=db,
        email=formulaire.username,
        password=formulaire.password,
    )

    if utilisateur is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé",
        )

    token = create_access_token(
        subject=str(utilisateur.user_id)
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }
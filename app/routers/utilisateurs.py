from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Utilisateur import Utilisateur
from app.schemas.utilisateurs import (
    UtilisateurInscription,
    UtilisateurLecture,
)
from app.security import get_current_user, hash_password


router = APIRouter(
    prefix="/users",
    tags=["Utilisateurs"],
)


@router.post(
    "/register",
    response_model=UtilisateurLecture,
    status_code=status.HTTP_201_CREATED,
)
def inscrire_utilisateur(
    donnees: UtilisateurInscription,
    db: Session = Depends(get_db),
):
    email_normalise = donnees.email.lower()

    utilisateur_existant = db.scalar(
        select(Utilisateur).where(
            Utilisateur.email == email_normalise
        )
    )

    if utilisateur_existant is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette adresse email est déjà utilisée",
        )

    utilisateur = Utilisateur(
        nom=donnees.nom.strip(),
        prenom=donnees.prenom.strip(),
        email=email_normalise,
        telephone=(
            donnees.telephone.strip()
            if donnees.telephone
            else None
        ),
        password_hash=hash_password(donnees.password),
        role="CLIENT",
        actif=True,
    )

    db.add(utilisateur)

    try:
        db.commit()
        db.refresh(utilisateur)

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible de créer cet utilisateur",
        )

    return utilisateur


@router.get(
    "/me",
    response_model=UtilisateurLecture,
)
def lire_mon_profil(
    utilisateur: Annotated[
        Utilisateur,
        Depends(get_current_user),
    ],
):
    return utilisateur
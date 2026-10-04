from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Logement import Logement
from app.models.Utilisateur import Utilisateur
from app.schemas.logements import (
    LogementCreation,
    LogementLecture,
    LogementModification,
)
from app.security import require_admin


router = APIRouter(
    prefix="/logements",
    tags=["Logements"],
)

DB = Annotated[Session, Depends(get_db)]
Admin = Annotated[Utilisateur, Depends(require_admin)]


@router.get(
    "",
    response_model=list[LogementLecture],
)
def lister_logements(
    db: DB,
    ville: str | None = Query(default=None),
    type_logement: str | None = Query(default=None),
    capacite_min: int | None = Query(default=None, ge=1),
    prix_max: float | None = Query(default=None, gt=0),
):
    requete = (
        select(Logement)
        .where(Logement.actif == True) 
        .order_by(Logement.prix_par_nuit)
    )

    if ville:
        requete = requete.where(
            func.lower(Logement.ville) == ville.strip().lower()
        )

    if type_logement:
        requete = requete.where(
            Logement.type_logement == type_logement.upper()
        )

    if capacite_min is not None:
        requete = requete.where(
            Logement.capacite >= capacite_min
        )

    if prix_max is not None:
        requete = requete.where(
            Logement.prix_par_nuit <= prix_max
        )

    return db.scalars(requete).all()


@router.get(
    "/{logement_id}",
    response_model=LogementLecture,
)
def obtenir_logement(
    logement_id: int,
    db: DB,
):
    logement = db.get(Logement, logement_id)

    if logement is None or not logement.actif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logement introuvable",
        )

    return logement


@router.post(
    "",
    response_model=LogementLecture,
    status_code=status.HTTP_201_CREATED,
)
def creer_logement(
    donnees: LogementCreation,
    db: DB,
    admin: Admin,
):
    logement = Logement(
        **donnees.model_dump()
    )

    db.add(logement)
    db.commit()
    db.refresh(logement)

    return logement


@router.patch(
    "/{logement_id}",
    response_model=LogementLecture,
)
def modifier_logement(
    logement_id: int,
    donnees: LogementModification,
    db: DB,
    admin: Admin,
):
    logement = db.get(Logement, logement_id)

    if logement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logement introuvable",
        )

    modifications = donnees.model_dump(
        exclude_unset=True,
    )

    for champ, valeur in modifications.items():
        setattr(logement, champ, valeur)

    db.commit()
    db.refresh(logement)

    return logement


@router.delete(
    "/{logement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def desactiver_logement(
    logement_id: int,
    db: DB,
    admin: Admin,
):
    logement = db.get(Logement, logement_id)

    if logement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logement introuvable",
        )

    logement.actif = False

    db.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
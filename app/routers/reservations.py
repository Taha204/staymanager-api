from datetime import date
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Logement import Logement
from app.models.Reservation import Reservation
from app.models.Utilisateur import Utilisateur
from app.schemas.reservations import (
    ReservationCreation,
    ReservationLecture,
)
from app.security import (
    get_current_user,
    require_admin,
)


router = APIRouter(
    prefix="/reservations",
    tags=["Réservations"],
)


DB = Annotated[
    Session,
    Depends(get_db),
]

UtilisateurConnecte = Annotated[
    Utilisateur,
    Depends(get_current_user),
]

Admin = Annotated[
    Utilisateur,
    Depends(require_admin),
]


@router.post(
    "",
    response_model=ReservationLecture,
    status_code=status.HTTP_201_CREATED,
)
def creer_reservation(
    donnees: ReservationCreation,
    db: DB,
    utilisateur: UtilisateurConnecte,
):
    logement = db.get(
        Logement,
        donnees.logement_id,
    )

    if logement is None or not logement.actif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "Logement introuvable "
                "ou indisponible"
            ),
        )

    if donnees.date_debut < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "La date de début ne peut "
                "pas être dans le passé"
            ),
        )

    if donnees.nombre_personnes > logement.capacite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Ce logement accepte au maximum "
                f"{logement.capacite} personne(s)"
            ),
        )

    requete_chevauchement = (
        select(Reservation)
        .where(
            Reservation.logement_id
            == donnees.logement_id,
            Reservation.statut
            == "CONFIRMEE",
            Reservation.date_debut
            < donnees.date_fin,
            Reservation.date_fin
            > donnees.date_debut,
        )
    )

    reservation_existante = db.scalar(
        requete_chevauchement
    )

    if reservation_existante is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Le logement est déjà réservé "
                "sur cette période"
            ),
        )

    nombre_nuits = (
        donnees.date_fin
        - donnees.date_debut
    ).days

    prix_total = (
        Decimal(nombre_nuits)
        * Decimal(str(logement.prix_par_nuit))
    )

    reservation = Reservation(
        user_id=utilisateur.user_id,
        logement_id=logement.logement_id,
        date_debut=donnees.date_debut,
        date_fin=donnees.date_fin,
        nombre_personnes=(
            donnees.nombre_personnes
        ),
        prix_total=prix_total,
        statut="CONFIRMEE",
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    return reservation


@router.get(
    "",
    response_model=list[ReservationLecture],
)
def lister_toutes_reservations(
    db: DB,
    admin: Admin,
    statut_reservation: (
        Literal[
            "CONFIRMEE",
            "ANNULEE",
            "TERMINEE",
        ]
        | None
    ) = None,
):
    requete = (
        select(Reservation)
        .order_by(
            Reservation.date_reservation.desc()
        )
    )

    if statut_reservation is not None:
        requete = requete.where(
            Reservation.statut
            == statut_reservation
        )

    return db.scalars(requete).all()


@router.get(
    "/me",
    response_model=list[ReservationLecture],
)
def mes_reservations(
    db: DB,
    utilisateur: UtilisateurConnecte,
):
    requete = (
        select(Reservation)
        .where(
            Reservation.user_id
            == utilisateur.user_id
        )
        .order_by(
            Reservation.date_reservation.desc()
        )
    )

    return db.scalars(requete).all()


@router.get(
    "/me/actuelles",
    response_model=list[ReservationLecture],
)
def mes_reservations_actuelles(
    db: DB,
    utilisateur: UtilisateurConnecte,
):
    requete = (
        select(Reservation)
        .where(
            Reservation.user_id
            == utilisateur.user_id,
            Reservation.statut
            == "CONFIRMEE",
            Reservation.date_fin
            >= date.today(),
        )
        .order_by(
            Reservation.date_debut
        )
    )

    return db.scalars(requete).all()


@router.get(
    "/me/historique",
    response_model=list[ReservationLecture],
)
def historique_reservations(
    db: DB,
    utilisateur: UtilisateurConnecte,
):
    requete = (
        select(Reservation)
        .where(
            Reservation.user_id
            == utilisateur.user_id,
            (
                (
                    Reservation.date_fin
                    < date.today()
                )
                | (
                    Reservation.statut
                    == "ANNULEE"
                )
            ),
        )
        .order_by(
            Reservation.date_debut.desc()
        )
    )

    return db.scalars(requete).all()


@router.patch(
    "/{reservation_id}/annuler",
    response_model=ReservationLecture,
)
def annuler_reservation(
    reservation_id: int,
    db: DB,
    utilisateur: UtilisateurConnecte,
):
    reservation = db.get(
        Reservation,
        reservation_id,
    )

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Réservation introuvable",
        )

    if (
        reservation.user_id
        != utilisateur.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Cette réservation ne "
                "vous appartient pas"
            ),
        )

    if reservation.statut == "ANNULEE":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cette réservation est "
                "déjà annulée"
            ),
        )

    if reservation.date_debut <= date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Une réservation commencée "
                "ne peut plus être annulée"
            ),
        )

    reservation.statut = "ANNULEE"

    db.commit()
    db.refresh(reservation)

    return reservation
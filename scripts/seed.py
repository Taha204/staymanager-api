from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models.Logement import Logement
from app.models.Reservation import Reservation
from app.models.Utilisateur import Utilisateur
from app.security import hash_password


def obtenir_ou_creer_utilisateur(
    db,
    nom,
    prenom,
    email,
    telephone,
    password,
    role,
):
    utilisateur = db.scalar(
        select(Utilisateur).where(
            Utilisateur.email == email
        )
    )

    if utilisateur is None:
        utilisateur = Utilisateur(
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            password_hash=hash_password(password),
            role=role,
            actif=True,
        )

        db.add(utilisateur)
        db.flush()

    return utilisateur


def obtenir_ou_creer_logement(
    db,
    titre,
    description,
    adresse,
    ville,
    type_logement,
    capacite,
    prix_par_nuit,
):
    logement = db.scalar(
        select(Logement).where(
            Logement.titre == titre
        )
    )

    if logement is None:
        logement = Logement(
            titre=titre,
            description=description,
            adresse=adresse,
            ville=ville,
            type_logement=type_logement,
            capacite=capacite,
            prix_par_nuit=Decimal(
                str(prix_par_nuit)
            ),
            actif=True,
        )

        db.add(logement)
        db.flush()

    return logement


def creer_reservation_si_absente(
    db,
    utilisateur,
    logement,
    date_debut,
    date_fin,
    nombre_personnes,
    statut,
):
    reservation = db.scalar(
        select(Reservation).where(
            Reservation.user_id
            == utilisateur.user_id,
            Reservation.logement_id
            == logement.logement_id,
            Reservation.date_debut
            == date_debut,
            Reservation.date_fin
            == date_fin,
        )
    )

    if reservation is not None:
        return reservation

    nombre_nuits = (
        date_fin - date_debut
    ).days

    reservation = Reservation(
        user_id=utilisateur.user_id,
        logement_id=logement.logement_id,
        date_debut=date_debut,
        date_fin=date_fin,
        nombre_personnes=nombre_personnes,
        prix_total=(
            Decimal(nombre_nuits)
            * Decimal(str(logement.prix_par_nuit))
        ),
        statut=statut,
    )

    db.add(reservation)

    return reservation


def seed():
    db = SessionLocal()

    try:
        admin = obtenir_ou_creer_utilisateur(
            db=db,
            nom="Admin",
            prenom="StayManager",
            email="admin@staymanager.fr",
            telephone="0600000001",
            password="Admin2026!",
            role="ADMIN",
        )

        client = obtenir_ou_creer_utilisateur(
            db=db,
            nom="Martin",
            prenom="Alice",
            email="alice@staymanager.fr",
            telephone="0600000002",
            password="Client2026!",
            role="CLIENT",
        )

        appartement = obtenir_ou_creer_logement(
            db=db,
            titre="Appartement Capitole",
            description=(
                "Appartement moderne situé "
                "dans le centre de Toulouse"
            ),
            adresse="10 place du Capitole",
            ville="Toulouse",
            type_logement="APPARTEMENT",
            capacite=4,
            prix_par_nuit=95,
        )

        studio = obtenir_ou_creer_logement(
            db=db,
            titre="Studio proche du métro",
            description=(
                "Studio équipé proche "
                "des transports"
            ),
            adresse="15 avenue des Minimes",
            ville="Toulouse",
            type_logement="STUDIO",
            capacite=2,
            prix_par_nuit=55,
        )

        maison = obtenir_ou_creer_logement(
            db=db,
            titre="Maison avec jardin",
            description=(
                "Maison familiale avec jardin"
            ),
            adresse="8 rue des Lilas",
            ville="Bordeaux",
            type_logement="MAISON",
            capacite=6,
            prix_par_nuit=140,
        )

        debut_future = date.today() + timedelta(
            days=30
        )

        creer_reservation_si_absente(
            db=db,
            utilisateur=client,
            logement=appartement,
            date_debut=debut_future,
            date_fin=debut_future + timedelta(days=4),
            nombre_personnes=2,
            statut="CONFIRMEE",
        )

        debut_passee = date.today() - timedelta(
            days=20
        )

        creer_reservation_si_absente(
            db=db,
            utilisateur=client,
            logement=studio,
            date_debut=debut_passee,
            date_fin=debut_passee + timedelta(days=3),
            nombre_personnes=1,
            statut="TERMINEE",
        )

        db.commit()

        print("Données de démonstration créées.")
        print("Admin : admin@staymanager.fr / Admin2026!")
        print("Client : alice@staymanager.fr / Client2026!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Reservation(Base):
    __tablename__ = "reservation"

    __table_args__ = (
        CheckConstraint(
            "date_fin > date_debut",
            name="ck_reservation_dates",
        ),
        CheckConstraint(
            "nombre_personnes > 0",
            name="ck_reservation_nb_personnes",
        ),
        CheckConstraint(
            "prix_total >= 0",
            name="ck_reservation_prix",
        ),
        CheckConstraint(
            "statut IN ('CONFIRMEE', 'ANNULEE', 'TERMINEE')",
            name="ck_reservation_statut",
        ),
        Index(
            "ix_reservation_logement_dates",
            "logement_id",
            "date_debut",
            "date_fin",
        ),
    )

    reservation_id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("utilisateur.user_id"),
        nullable=False,
        index=True,
    )

    logement_id: Mapped[int] = mapped_column(
        ForeignKey("logement.logement_id"),
        nullable=False,
        index=True,
    )

    date_debut: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    date_fin: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    nombre_personnes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    prix_total: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    statut: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="CONFIRMEE",
        server_default="CONFIRMEE",
    )

    date_reservation: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    utilisateur: Mapped["Utilisateur"] = relationship(
        back_populates="reservations",
    )

    logement: Mapped["Logement"] = relationship(
        back_populates="reservations",
    )
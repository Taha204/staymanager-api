from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Identity,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Logement(Base):
    __tablename__ = "logement"

    __table_args__ = (
        CheckConstraint(
            "type_logement IN "
            "('STUDIO', 'APPARTEMENT', 'MAISON', 'CHAMBRE')",
            name="ck_logement_type",
        ),
        CheckConstraint(
            "capacite > 0",
            name="ck_logement_capacite",
        ),
        CheckConstraint(
            "prix_par_nuit > 0",
            name="ck_logement_prix",
        ),
    )

    logement_id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    titre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    adresse: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    ville: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    type_logement: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    capacite: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    prix_par_nuit: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    actif: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    date_creation: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="logement",
    )
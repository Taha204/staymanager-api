from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Identity,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateur"

    __table_args__ = (
        CheckConstraint(
            "role IN ('CLIENT', 'ADMIN')",
            name="ck_utilisateur_role",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        Identity(),
        primary_key=True,
    )

    nom: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    prenom: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    telephone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="CLIENT",
        server_default="CLIENT",
    )

    actif: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )

    date_inscription: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    reservations: Mapped[list["Reservation"]] = relationship(
        back_populates="utilisateur",
    )
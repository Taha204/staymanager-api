from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


StatutReservation = Literal[
    "CONFIRMEE",
    "ANNULEE",
    "TERMINEE",
]


class ReservationCreation(BaseModel):
    logement_id: int = Field(
        gt=0,
        examples=[1],
    )

    date_debut: date = Field(
        examples=["2026-10-10"],
    )

    date_fin: date = Field(
        examples=["2026-10-15"],
    )

    nombre_personnes: int = Field(
        gt=0,
        le=50,
        examples=[2],
    )

    @model_validator(mode="after")
    def verifier_dates(self):
        if self.date_fin <= self.date_debut:
            raise ValueError(
                "La date de fin doit être postérieure "
                "à la date de début"
            )

        return self


class ReservationLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reservation_id: int
    user_id: int
    logement_id: int
    date_debut: date
    date_fin: date
    nombre_personnes: int
    prix_total: Decimal
    statut: StatutReservation
    date_reservation: datetime
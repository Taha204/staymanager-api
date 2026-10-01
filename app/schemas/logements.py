from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TypeLogement = Literal[
    "STUDIO",
    "APPARTEMENT",
    "MAISON",
    "CHAMBRE",
]


class LogementBase(BaseModel):
    titre: str = Field(
        min_length=3,
        max_length=200,
        examples=["Studio proche du centre de Toulouse"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    adresse: str = Field(
        min_length=5,
        max_length=255,
        examples=["10 rue des Fleurs"],
    )

    ville: str = Field(
        min_length=2,
        max_length=100,
        examples=["Toulouse"],
    )

    type_logement: TypeLogement

    capacite: int = Field(
        gt=0,
        le=50,
        examples=[2],
    )

    prix_par_nuit: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
        examples=[75.50],
    )


class LogementCreation(LogementBase):
    pass


class LogementModification(BaseModel):
    titre: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    adresse: str | None = Field(
        default=None,
        min_length=5,
        max_length=255,
    )

    ville: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    type_logement: TypeLogement | None = None

    capacite: int | None = Field(
        default=None,
        gt=0,
        le=50,
    )

    prix_par_nuit: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
    )

    actif: bool | None = None


class LogementLecture(LogementBase):
    model_config = ConfigDict(from_attributes=True)

    logement_id: int
    actif: bool
    date_creation: datetime
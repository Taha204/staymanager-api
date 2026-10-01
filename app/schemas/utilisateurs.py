from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class UtilisateurInscription(BaseModel):
    nom: str = Field(
        min_length=2,
        max_length=100,
        examples=["Mourad"],
    )

    prenom: str = Field(
        min_length=2,
        max_length=100,
        examples=["Taha"],
    )

    email: EmailStr = Field(
        examples=["taha@gmail.com"],
    )

    telephone: str | None = Field(
        default=None,
        min_length=6,
        max_length=30,
        pattern=r"^[0-9+ .()\-]+$",
        examples=["+33 6 12 34 56 78"],
    )

    password: str = Field(
        min_length=8,
        max_length=128,
        examples=["MotDePasse2026!"],
    )


class UtilisateurLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    nom: str
    prenom: str
    email: EmailStr
    telephone: str | None
    role: str
    actif: bool
    date_inscription: datetime
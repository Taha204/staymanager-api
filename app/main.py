from fastapi import FastAPI
from sqlalchemy import text

from app.database import engine
from app.routers import auth, logements, utilisateurs, reservations

app = FastAPI(
    title="StayManager API",
    description="API de gestion et de réservation de logements",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(utilisateurs.router)
app.include_router(logements.router)    
app.include_router(reservations.router)

@app.get("/health", tags=["Santé"])
def health():
    return {"status": "ok"}


@app.get("/health/database", tags=["Santé"])
def health_database():
    with engine.connect() as connexion:
        utilisateur = connexion.execute(
            text("SELECT USER FROM dual")
        ).scalar()

    return {
        "status": "ok",
        "database": "Oracle",
        "user": utilisateur,
    }   
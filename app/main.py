from fastapi import FastAPI

app = FastAPI(
    title="StayManager API",
    description="API de gestion et de réservation de logements",
    version="1.0.0",
)


@app.get("/health", tags=["Santé"])
def health():
    return {"status": "ok"}
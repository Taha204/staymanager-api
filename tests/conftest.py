from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import engine
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def headers_auth(client):
    email = f"pytest-{uuid4().hex[:8]}@example.com"
    user_id = None

    reponse = client.post(
        "/users/register",
        json={
            "nom": "Test",
            "prenom": "Pytest",
            "email": email,
            "telephone": "0600000000",
            "password": "MotDePasse2026!",
        },
    )

    assert reponse.status_code == 201
    user_id = reponse.json()["user_id"]

    reponse = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": "MotDePasse2026!",
        },
    )

    assert reponse.status_code == 200

    token = reponse.json()["access_token"]

    yield {
        "Authorization": f"Bearer {token}"
    }

    # Nettoyage après les tests
    with engine.begin() as connexion:
        connexion.execute(
            text(
                """
                DELETE FROM reservation
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id},
        )

        connexion.execute(
            text(
                """
                DELETE FROM utilisateur
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id},
        )
def test_route_protegee_sans_token_renvoie_401(client):
    reponse = client.get("/users/me")

    assert reponse.status_code == 401


def test_connexion_incorrecte_renvoie_401(client):
    reponse = client.post(
        "/auth/token",
        data={
            "username": "inexistant@example.com",
            "password": "MauvaisMotDePasse",
        },
    )

    assert reponse.status_code == 401
    assert reponse.json() == {
        "detail": "Email ou mot de passe incorrect"
    }


def test_token_sans_username_renvoie_422(client):
    reponse = client.post(
        "/auth/token",
        data={
            "password": "MotDePasse2026!",
        },
    )

    assert reponse.status_code == 422
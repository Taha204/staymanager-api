def test_creer_reservation_sans_token_renvoie_401(client):
    reponse = client.post(
        "/reservations",
        json={
            "logement_id": 1,
            "date_debut": "2026-12-10",
            "date_fin": "2026-12-15",
            "nombre_personnes": 2,
        },
    )

    assert reponse.status_code == 401

def test_dates_reservation_invalides_renvoient_422(
    client,
    headers_auth,
):
    reponse = client.post(
        "/reservations",
        headers=headers_auth,
        json={
            "logement_id": 1,
            "date_debut": "2026-12-15",
            "date_fin": "2026-12-10",
            "nombre_personnes": 2,
        },
    )

    assert reponse.status_code == 422


def test_nombre_personnes_invalide_renvoie_422(
    client,
    headers_auth,
):
    reponse = client.post(
        "/reservations",
        headers=headers_auth,
        json={
            "logement_id": 1,
            "date_debut": "2026-12-10",
            "date_fin": "2026-12-15",
            "nombre_personnes": 0,
        },
    )

    assert reponse.status_code == 422
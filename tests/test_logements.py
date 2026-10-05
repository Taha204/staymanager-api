def test_lire_logement_existant(client):
    reponse = client.get("/logements/1")

    assert reponse.status_code == 200
    assert reponse.json()["logement_id"] == 1


def test_lire_logement_inexistant_renvoie_404(client):
    reponse = client.get("/logements/999999")

    assert reponse.status_code == 404
    assert reponse.json() == {
        "detail": "Logement introuvable"
    }


def test_id_logement_non_numerique_renvoie_422(client):
    reponse = client.get("/logements/abc")

    assert reponse.status_code == 422


def test_lister_logements(client):
    reponse = client.get("/logements")

    assert reponse.status_code == 200
    assert isinstance(reponse.json(), list)


def test_filtrer_logements_par_ville(client):
    reponse = client.get(
        "/logements",
        params={"ville": "Toulouse"},
    )

    assert reponse.status_code == 200

    for logement in reponse.json():
        assert logement["ville"].lower() == "toulouse"


def test_capacite_invalide_renvoie_422(client):
    reponse = client.get(
        "/logements",
        params={"capacite_min": 0},
    )

    assert reponse.status_code == 422
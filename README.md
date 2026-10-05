    # StayManager API

    API REST sécurisée de gestion et de réservation de logements, réalisée dans le cadre du mini-projet **Introduction aux structures BDD Data et API**.

    > **NOM :** Taha MOURAD 
    > **Année universitaire :** 2026-2027

    ## 1. Présentation

    StayManager permet à des utilisateurs de rechercher et réserver des logements en ligne. L'application gère également les disponibilités, la capacité des logements, les conflits de dates, le calcul du prix et l'historique des réservations.

    Le projet met en œuvre :

    - Oracle pour la persistance des données ;
    - FastAPI pour l'API REST et la documentation Swagger ;
    - SQLAlchemy comme ORM ;
    - Alembic pour les migrations du schéma ;
    - Pydantic pour la validation des entrées et sorties ;
    - JWT et Argon2 pour l'authentification et la sécurité ;
    - Docker Compose pour exécuter l'API et Oracle ensemble ;
    - pytest pour les tests automatisés.

    ## 2. Fonctionnalités

    ### Utilisateurs

    - inscription d'un client ;
    - authentification par email et mot de passe ;
    - génération d'un token JWT ;
    - consultation du profil connecté ;
    - rôles `CLIENT` et `ADMIN` ;
    - consultation de tous les utilisateurs par un administrateur.

    ### Logements

    - consultation de la liste des logements actifs ;
    - consultation du détail d'un logement ;
    - filtres par ville, type, capacité minimale et prix maximal ;
    - création et modification par un administrateur ;
    - désactivation logique d'un logement par un administrateur.

    ### Réservations

    - réservation d'un logement par un utilisateur connecté ;
    - contrôle de la capacité ;
    - interdiction des périodes situées dans le passé ;
    - détection des chevauchements de réservations ;
    - calcul automatique du nombre de nuits et du prix total ;
    - consultation des réservations actuelles et de l'historique ;
    - annulation d'une réservation future ;
    - consultation de toutes les réservations par un administrateur.

    ## 3. Architecture

    ```mermaid
    flowchart LR
        U[Client HTTP / Swagger] --> A[API FastAPI]
        A --> P[Pydantic]
        A --> S[SQLAlchemy]
        S --> O[(Oracle FREEPDB1)]
        M[Alembic] --> O
    ```

    L'API et Oracle fonctionnent dans deux conteneurs distincts. Dans le réseau Docker Compose, l'API contacte la base avec le nom de service `oracle` sur le port `1521`.

    ## 4. Modèle de données

    ```mermaid
    erDiagram
        UTILISATEUR ||--o{ RESERVATION : effectue
        LOGEMENT ||--o{ RESERVATION : concerne

        UTILISATEUR {
            int user_id PK
            string nom
            string prenom
            string email UK
            string telephone
            string password_hash
            string role
            boolean actif
            datetime date_inscription
        }

        LOGEMENT {
            int logement_id PK
            string titre
            string description
            string adresse
            string ville
            string type_logement
            int capacite
            decimal prix_par_nuit
            boolean actif
            datetime date_creation
        }

        RESERVATION {
            int reservation_id PK
            int user_id FK
            int logement_id FK
            date date_debut
            date date_fin
            int nombre_personnes
            decimal prix_total
            string statut
            datetime date_reservation
        }
    ```

    Relations :

    - un utilisateur peut effectuer plusieurs réservations ;
    - un logement peut être réservé plusieurs fois à des périodes différentes ;
    - chaque réservation appartient à un seul utilisateur et concerne un seul logement.

    ## 5. Règles métier

    - `date_fin` doit être strictement postérieure à `date_debut` ;
    - une réservation ne peut pas commencer dans le passé ;
    - le nombre de personnes ne peut pas dépasser la capacité du logement ;
    - deux réservations confirmées d'un même logement ne peuvent pas se chevaucher ;
    - le prix total est calculé avec la formule :

    ```text
    prix_total = nombre_de_nuits × prix_par_nuit
    ```

    - une réservation commencée ne peut plus être annulée ;
    - une réservation annulée ne bloque plus les dates correspondantes ;
    - les logements sont désactivés logiquement afin de conserver l'historique.

    ## 6. Technologies

    | Technologie | Utilisation |
    |---|---|
    | Python 3.13 | Langage principal |
    | FastAPI | Développement de l'API REST |
    | Pydantic | Validation et sérialisation des données |
    | SQLAlchemy | Mapping objet-relationnel et requêtes |
    | Alembic | Versionnement du schéma Oracle |
    | Oracle Free | Base de données relationnelle |
    | python-oracledb | Pilote Python pour Oracle |
    | PyJWT | Création et validation des tokens JWT |
    | pwdlib / Argon2 | Hachage sécurisé des mots de passe |
    | pytest | Tests automatisés |
    | Docker Compose | Orchestration de l'API et de la base |

    ## 7. Arborescence

    ```text
    staymanager-api/
    ├── alembic/
    │   ├── versions/
    │   └── env.py
    ├── app/
    │   ├── models/
    │   │   ├── Utilisateur.py
    │   │   ├── Logement.py
    │   │   └── Reservation.py
    │   ├── routers/
    │   │   ├── auth.py
    │   │   ├── utilisateurs.py
    │   │   ├── logements.py
    │   │   └── reservations.py
    │   ├── schemas/
    │   │   ├── auth.py
    │   │   ├── utilisateurs.py
    │   │   ├── logements.py
    │   │   └── reservations.py
    │   ├── database.py
    │   ├── main.py
    │   └── security.py
    ├── scripts/
    │   └── seed.py
    ├── tests/
    │   ├── conftest.py
    │   ├── test_auth.py
    │   ├── test_logements.py
    │   └── test_reservations.py
    ├── .dockerignore
    ├── .env.example
    ├── .gitignore
    ├── alembic.ini
    ├── compose.yaml
    ├── Dockerfile
    ├── requirements.txt
    └── README.md
    ```

    ## 8. Prérequis

    - Git ;
    - Docker Desktop ;
    - Python 3.13 pour l'exécution locale ;
    - DBeaver est optionnel pour inspecter Oracle.

    ## 9. Configuration

    Copier le fichier d'exemple :

    ```powershell
    Copy-Item .env.example .env
    ```

    Puis remplacer les valeurs dans `.env` :

    ```env
    ORACLE_PASSWORD=ChangeMe123!
    APP_USER=staymanager
    APP_USER_PASSWORD=ChangeMe123!

    DB_DSN=localhost:1521/FREEPDB1
    DATABASE_URL=oracle+oracledb://staymanager:ChangeMe123!@localhost:1521/?service_name=FREEPDB1

    JWT_SECRET_KEY=remplacer_par_une_cle_secrete_longue
    JWT_ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```

    Une clé JWT peut être générée avec :

    ```powershell
    python -c "import secrets; print(secrets.token_urlsafe(64))"
    ```

    Le fichier `.env` contient des secrets et ne doit jamais être ajouté à Git.

    ## 10. Démarrage avec Docker Compose

    Construire et démarrer l'API et Oracle :

    ```powershell
    docker compose up -d --build
    ```

    Vérifier leur état :

    ```powershell
    docker compose ps
    ```

    La base doit apparaître avec l'état `healthy`.

    Consulter les logs :

    ```powershell
    docker compose logs -f api
    docker compose logs -f oracle
    ```

    Arrêter les conteneurs sans supprimer les données :

    ```powershell
    docker compose down
    ```

    > La commande `docker compose down -v` supprime également le volume Oracle et toutes les données. Elle ne doit être utilisée que pour repartir volontairement de zéro.

    ## 11. Migrations Alembic

    Au démarrage du conteneur API, la commande suivante est exécutée automatiquement :

    ```powershell
    python -m alembic upgrade head
    ```

    Commandes utiles en local :

    ```powershell
    # Afficher la migration appliquée
    python -m alembic current

    # Créer une migration après modification des modèles
    python -m alembic revision --autogenerate -m "description"

    # Appliquer les migrations
    python -m alembic upgrade head

    # Revenir d'une migration
    python -m alembic downgrade -1
    ```

    Alembic est l'unique mécanisme utilisé pour faire évoluer le schéma. Les tables ne sont pas créées avec `Base.metadata.create_all()`.

    ## 12. Données de démonstration

    Oracle doit être démarré avant l'exécution du script :

    ```powershell
    docker compose up -d oracle
    python -m scripts.seed
    ```

    Le script est idempotent : il peut être relancé sans recréer les mêmes données.

    Comptes de démonstration :

    | Rôle | Email | Mot de passe |
    |---|---|---|
    | Administrateur | `admin@staymanager.fr` | `Admin2026!` |
    | Client | `alice@staymanager.fr` | `Client2026!` |

    Ces comptes sont exclusivement destinés à la démonstration locale.

    ## 13. Documentation Swagger

    Lorsque l'API est démarrée :

    - Swagger UI : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
    - OpenAPI JSON : [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)
    - Santé de l'API : [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
    - Santé de la base : [http://127.0.0.1:8000/health/database](http://127.0.0.1:8000/health/database)

    ### Authentification dans Swagger

    1. Exécuter `POST /auth/token` avec l'email dans le champ `username`.
    2. Copier le token retourné, ou cliquer directement sur **Authorize**.
    3. Saisir les identifiants du compte.
    4. Tester les routes protégées.

    ## 14. Principales routes

    ### Authentification et utilisateurs

    | Méthode | Route | Accès | Description |
    |---|---|---|---|
    | POST | `/users/register` | Public | Inscription d'un client |
    | POST | `/auth/token` | Public | Connexion et génération JWT |
    | GET | `/users/me` | Connecté | Profil de l'utilisateur courant |
    | GET | `/users` | Admin | Liste des utilisateurs |

    ### Logements

    | Méthode | Route | Accès | Description |
    |---|---|---|---|
    | GET | `/logements` | Public | Liste et recherche des logements |
    | GET | `/logements/{id}` | Public | Détail d'un logement |
    | POST | `/logements` | Admin | Création d'un logement |
    | PATCH | `/logements/{id}` | Admin | Modification d'un logement |
    | DELETE | `/logements/{id}` | Admin | Désactivation logique |

    Filtres disponibles :

    ```text
    GET /logements?ville=Toulouse
    GET /logements?type_logement=APPARTEMENT
    GET /logements?capacite_min=2&prix_max=100
    ```

    ### Réservations

    | Méthode | Route | Accès | Description |
    |---|---|---|---|
    | POST | `/reservations` | Connecté | Créer une réservation |
    | GET | `/reservations/me` | Connecté | Toutes mes réservations |
    | GET | `/reservations/me/actuelles` | Connecté | Réservations confirmées actuelles/futures |
    | GET | `/reservations/me/historique` | Connecté | Réservations terminées ou annulées |
    | PATCH | `/reservations/{id}/annuler` | Propriétaire | Annuler une réservation future |
    | GET | `/reservations` | Admin | Consulter toutes les réservations |

    Filtre administrateur :

    ```text
    GET /reservations?statut_reservation=CONFIRMEE
    ```

    ## 15. Sécurité

    - les mots de passe ne sont jamais enregistrés en clair ;
    - ils sont hachés avec Argon2 ;
    - l'API retourne un token JWT signé et limité dans le temps ;
    - les routes protégées utilisent le schéma OAuth2 Bearer ;
    - les autorisations sont contrôlées avec les rôles `CLIENT` et `ADMIN` ;
    - les utilisateurs désactivés ne peuvent pas se connecter ;
    - les emails sont normalisés en minuscules ;
    - les paramètres SQL sont générés par SQLAlchemy, ce qui limite les risques d'injection SQL ;
    - le schéma Pydantic empêche l'exposition de `password_hash` ;
    - les secrets sont placés dans `.env`, exclu de Git.

    ## 16. Tests automatisés

    Les tests utilisent `TestClient` pour appeler directement l'application FastAPI. Oracle doit être démarré, mais Uvicorn n'est pas nécessaire.

    ```powershell
    docker compose up -d oracle
    python -m pytest -v
    ```

    Les tests couvrent notamment :

    - l'accès sans token ;
    - les identifiants incorrects ;
    - la validation OAuth2 ;
    - la lecture et les filtres des logements ;
    - les identifiants de route invalides ;
    - la validation des dates et du nombre de personnes.

    Résultat de référence :

    ```text
    12 passed
    ```

    ## 17. Codes HTTP utilisés

    | Code | Signification dans le projet |
    |---|---|
    | 200 | Requête exécutée avec succès |
    | 201 | Ressource créée |
    | 204 | Logement désactivé, sans corps de réponse |
    | 400 | Règle métier non respectée |
    | 401 | Authentification absente ou invalide |
    | 403 | Droits insuffisants |
    | 404 | Ressource introuvable |
    | 409 | Conflit : email existant, chevauchement ou annulation répétée |
    | 422 | Données invalides selon Pydantic/FastAPI |

    ## 18. Scénario de démonstration

    1. Démarrer le projet avec Docker Compose.
    2. Ouvrir Swagger.
    3. Vérifier `/health/database`.
    4. Afficher et filtrer les logements.
    5. Se connecter comme client.
    6. Consulter `/users/me`.
    7. Créer une réservation.
    8. Tenter une deuxième réservation chevauchante et montrer le `409`.
    9. Consulter les réservations actuelles et l'historique.
    10. Annuler une réservation future.
    11. Se connecter comme administrateur.
    12. Créer ou modifier un logement.
    13. Afficher tous les utilisateurs et toutes les réservations.
    14. Lancer `pytest` et présenter les tests réussis.

    ## 19. Commandes utiles

    ```powershell
    # Construire et démarrer
    docker compose up -d --build

    # Reconstruire seulement l'API après modification
    docker compose up -d --build api

    # État des services
    docker compose ps

    # Logs de l'API
    docker compose logs -f api

    # Données de démonstration
    python -m scripts.seed

    # Tests
    python -m pytest -v

    # Migration actuelle
    python -m alembic current

    # Arrêt sans perte des données
    docker compose down
    ```

    ## 20. Limites et améliorations possibles

    - ajout d'un système de paiement ;
    - ajout de photos de logements ;
    - pagination des listes ;
    - ajout d'avis et de notes ;
    - envoi d'emails de confirmation ;
    - renouvellement des tokens ;
    - verrouillage transactionnel renforcé en cas de réservations simultanées ;
    - automatisation du passage de `CONFIRMEE` à `TERMINEE` ;
    - intégration continue exécutant automatiquement les tests.

    ## 21. Conclusion

    StayManager répond aux objectifs du mini-projet en proposant une base Oracle structurée et sécurisée, une API FastAPI documentée, des modèles SQLAlchemy, des migrations Alembic, une validation Pydantic, une authentification JWT, une orchestration Docker Compose et des tests automatisés.

    Le projet sépare clairement la persistance, les modèles, les schémas d'échange, les routes, la sécurité, les migrations et les tests afin de faciliter sa maintenance et son évolution.

# Étape 5 v2 — vérifications réelles du 4 novembre 2026

Statut : terminée. Poste de Matis, utilisateur MATIS_DOUAY, SYSADMIN, SIDEFLIX_WH, contexte SIDEFLIX.BRONZE. Étapes 1–4 vérifiées dans la passation et les preuves existantes ; aucune commande Terraform exécutée.

## Méthodes et résultats

- **5.1 — TD 2B : watermark/MERGE** : `ingestion/incremental_catalog.py` lit le catalogue PostgreSQL réel. Premier passage : 6 lignes mises à jour, 0 insertion, total 6 ; rejeu : 0 extraction et 0 modification. Identifiants IMDb, provenance et métadonnées conservés. Watermark strict `updated_at > MAX(updated_at)` du TD : il suppose des dates de modification fiables et ne traite pas les suppressions.
- **5.2 — TD 2B : mise à jour contrôlée** : `ingestion/verify_catalog_replay.py` travaille exclusivement sur deux copies LAB. Résultats : 6 insertions, rejeu 0, modification d'un titre 1 update, restauration 1 update, dernier rejeu 0. Comparaison intégrale avant/après : catalogues réels PostgreSQL et Snowflake inchangés. La première tentative du contrôle a échoué car la table de test PostgreSQL n'était pas encore commitée ; corrigé en exécutant les DDL hors transaction englobante. Aucun changement aux données réelles.
- **5.3 — TD 2A et pack 05** : `ingestion/load_sessions.py` charge fichiers par PUT/stage/COPY et appelle réellement les deux APIs avec le collecteur `requests` existant, puis PARSE_JSON/VARIANT. Les réponses reçues sont sauvegardées localement dans `source/real/api_runs/`, hors Git. L'identité IMDb des six entités et les sept jours par article sont vérifiés. MERGE des réponses sur lot/URL pour éviter les doublons.
- **5.4 — réconciliation et rejeu** : `ingestion/verify_bronze_v2.py`. Empreintes de tous les fichiers du manifeste initial inchangées. Les APIs sont de nouveaux appels, distingués de ces anciens snapshots par leurs propres empreintes de lot. Chaque ligne a SOURCE_SYSTEM, _BATCH_ID, _source_file et _loaded_at (session UTC), reliés au journal PUBLIC_SOURCE_RUNS. Rejeu des fichiers et des réponses exactes : zéro nouvelle ligne sur les six lots. COPY effectivement rejoué sans FORCE : « 0 files processed » pour les quatre lots fichiers. Grains/clés uniques vérifiés ci-dessous.

| Source | Grain chargé et volume vérifié | Méthode |
| --- | --- | --- |
| IMDb | 6 œuvres, 6 tconst distincts | PUT/COPY, sélection de six lignes du fichier source |
| MovieLens | 6 films + 6 liens + 74 notes uniques userId/movieId = 86 lignes | PUT/COPY, sous-ensemble réel lié au mapping |
| Netflix Top 10 | 3 lignes uniques semaine/catégorie/titre/saison pour Sicario/Get Out | PUT/COPY ; seul Sicario est confirmé dans le mapping, les autres correspondances restent non jointes |
| Wikidata | 6 réponses, 6 URLs distinctes | API réelle → VARIANT |
| Wikimedia | 6 réponses, 42 observations article/jour distinctes, 26/10–01/11/2026 | API réelle → VARIANT |
| Sessions Sideflix **simulées** | 32 lignes, 31 session_id distincts, 1 durée négative | PUT/COPY ; ne compte pas parmi les cinq jeux réels |

Bronze SESSIONS_RAW conserve aussi les 32 lignes du prototype. Les 32 lignes v2 sont identifiées par SOURCE_SYSTEM=sessions_simulated et leur lot ; dbt v2 devra filtrer ce périmètre avant dédoublonnage. Les autres archives restent en LAB. Le journal enregistre également les rejeux réussis avec 0 ligne chargée ; il n'est pas censé garder un nombre fixe d'exécutions.

## Reproduction

Depuis la racine, avec les variables Snowflake/RSA et PG* configurées localement :

```sh
python -m venv .venv
.venv/bin/python -m pip install -r ingestion/requirements.txt
.venv/bin/python ingestion/check_connection.py
.venv/bin/python ingestion/incremental_catalog.py
.venv/bin/python ingestion/verify_catalog_replay.py
.venv/bin/python ingestion/load_sessions.py --public --api-mode live --receipt rendu/ingestion_v2_initial.json
.venv/bin/python ingestion/load_sessions.py --public --replay-receipt rendu/ingestion_v2_initial.json --receipt rendu/ingestion_v2_replay.json
.venv/bin/python ingestion/verify_bronze_v2.py
```

Le rejeu exact nécessite les réponses locales `api_runs` de ce poste ; à défaut, effectuer une collecte réelle et produire un nouveau reçu, sans prétendre retrouver le snapshot précédent. Les nouveaux snapshots peuvent différer et doivent être documentés. Aucun secret versionné. Connector 4.8.0 et cryptography 46.0.5 comme dans le pack ; détection de plateforme explicitement désactivée avant import (voir preuve d'accès), aucun accès aux métadonnées d'instance nécessaire.

## Preuves brutes

- `python_connexion_matis.txt`
- `python_5_v2_catalog_initial.txt`, `python_5_v2_catalog_replay.txt`, `python_5_v2_catalog_lab.txt`
- `python_5_v2_sources_initial.txt`, `python_5_v2_sources_replay.txt`
- `ingestion_v2_initial.json`, `ingestion_v2_replay.json` : lots et attendus, aucune donnée privée
- `python_5_v2_reconciliation.txt` : tous les contrôles réussis

Suite : étape 6, adapter et exécuter dbt sur ces données v2 ; les anciens résultats dbt restent historiques.

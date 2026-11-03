# Étape 5 : chargement réel des deux sources en Bronze (3 novembre 2026)

Session de Jérémy Caillaud, avec assistance de l'IA. Sources : plan scolaire (étape 5), TD 2 (onprem-to-snowflake) parties A (batch : stage + COPY INTO) et B (incrémental : watermark + MERGE), scripts de l'étape 3 (Matis).

## 5.0 Prérequis : base PostgreSQL `sideflix` recréée sur le poste de Jérémy

- PostgreSQL 17 (service `postgresql-x64-17`), utilisateur `postgres`. Scripts de Matis exécutés sans modification : `source/01_create_catalog.sql` (6 contenus A à F) puis `source/02_verify_catalog.sql` (3 contrôles OK, 6 contenus après ROLLBACK).
- Preuves : `rendu/postgresql_5_0_create_catalog_jeremy.txt`, `rendu/postgresql_5_0_verify_catalog_jeremy.txt`. Cette fois, le contrôle est exécuté directement depuis le fichier du dépôt.

## 5.1 et 5.2 Catalogue : ingestion incrémentale (watermark + MERGE)

- `ingestion/incremental_catalog.py`, adapté de `incremental_orders.py` (TD 2 partie B) : watermark = `MAX(updated_at)` dans `SIDEFLIX.BRONZE.CATALOG` ; extraction `WHERE updated_at > watermark` dans `public.catalog` ; table temporaire `CATALOG_BATCH` puis `MERGE` sur `content_id` ; journal dans `SIDEFLIX.BRONZE.LOAD_RUNS`. Les tables cibles existent depuis l'action 4.3 (le script ne les crée pas).

| Run | Situation | Attendu | Obtenu | Preuve |
| --- | --- | --- | --- | --- |
| 1 | premier chargement | watermark 1900, 6 extraites, 6 insérées, 6 contenus | identique | `rendu/python_5_1_run1_premier_chargement.txt` |
| 2 | relance sans changement (B1 du TD 2) | 0 extraite, rien de nouveau, 6 contenus | identique (watermark 2026-10-29T12:00:00Z) | `rendu/python_5_2a_run2_replay.txt` |
| 3 | titre de B modifié dans PostgreSQL (trigger `updated_at`) | 1 extraite, 0 insérée, 1 mise à jour, 6 contenus distincts | identique | `rendu/python_5_2_run3_mise_a_jour_titre.txt` |

Changement volontaire et conservé : le titre de B est « Dernier Metro (version restauree) » dans PostgreSQL et dans Snowflake. Aucun effet sur les indicateurs (calculés par `content_id`).

## 5.3 et 5.4 Sessions : chargement batch (stage + COPY INTO)

- `ingestion/load_sessions.py`, adapté de la partie A du TD 2 : `PUT` des trois fichiers JSON sur `SESSIONS_STAGE` (au TD 2 le dépôt se faisait à la main ; le TD indique qu'un job le fait par `PUT` en entreprise, ce qui rend le chargement relançable par Airflow à l'étape 8), puis `COPY INTO SESSIONS_RAW` avec `raw` (VARIANT), `_source_file` (`METADATA$FILENAME`) et `_loaded_at`.

| Exécution | Attendu | Obtenu | Preuve |
| --- | --- | --- | --- |
| 1 | 3 fichiers UPLOADED puis LOADED ; 3 + 15 + 14 = 32 lignes | identique | `rendu/python_5_3_load_sessions_run1.txt` |
| 2 (replay) | PUT SKIPPED, COPY 0 fichier traité, toujours 32 lignes | identique | `rendu/python_5_4_load_sessions_replay.txt` |

## Contrôle final dans Snowflake

`ingestion/02_check_bronze.sql` (lecture seule) compare attendu et obtenu : **10 contrôles sur 10 OK** (6 contenus distincts, titre de B, 3 exécutions journalisées avec 6 / 0 / 1 lignes extraites, 32 lignes brutes issues de 3 fichiers, 31 `session_id` distincts, doublon S4 présent 2 fois, S31 à -60 s conservée). Preuve : `rendu/snowflake_5_check_bronze.csv`.

Les anomalies volontaires (doublon S4, durée négative S31) sont bien présentes en Bronze : elles seront traitées dans Silver (dédoublonnage et quarantaine, étape 6).

## Limites à présenter à l'oral

- Watermark sur `updated_at`, repris du TD 2 : une suppression dans PostgreSQL n'est pas détectée et une modification qui ne change pas `updated_at` n'est pas reprise. Le prototype démontre chargement initial, mise à jour et replay ; ce n'est pas un CDC complet (lecture du journal de transactions).
- La relance du COPY est protégée par les métadonnées de chargement de Snowflake (64 jours) et seulement pour des fichiers de même nom ; un fichier renommé serait rechargé (question 1 du TD 2).
- La base PostgreSQL est locale au poste qui lance l'ingestion ; utilisateur Snowflake `REDGRAVE_AIRFLOW` (droits trop larges, voir action 4.2).
- Le connecteur Snowflake affiche un `FutureWarning` sans effet.

## Reproduction

PowerShell, dossier `Sideflix`, PostgreSQL et Python 3.11 :
1. Variables : `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PRIVATE_KEY_FILE` (voir `ingestion/.env.example`), `PGUSER`, `PGPASSWORD` ; ajouter `C:\Program Files\PostgreSQL\17\bin` au PATH.
2. `createdb -h 127.0.0.1 sideflix`, puis `psql ... -f source/01_create_catalog.sql` et `-f source/02_verify_catalog.sql`.
3. `python ingestion/incremental_catalog.py` (deux fois), modification d'un titre avec `psql`, puis une troisième fois.
4. `python ingestion/load_sessions.py` (deux fois).
5. Snowsight, rôle SYSADMIN : `ingestion/02_check_bronze.sql`, attendu 10 OK.

## Prochaine étape

Étape 6 : projet dbt Sideflix (6.1), puis `silver_catalog` et `stg_sessions` (6.2), quarantaine (6.3), `silver_sessions` dédoublonnée (6.4), `gold_content_daily` et classement (6.5).

# Action 4.3 : couche Bronze (format JSON, stage interne, tables) et connexion par clé (3 novembre 2026)

Session de Jérémy Caillaud, avec assistance de l'IA. Sources : plan scolaire (étape 4), `02_snowflake_setup.sql` et `incremental_orders.py` du TD 2 (onprem-to-snowflake), cours 4.2 (schema on read).

## Réalisé

- `ingestion/01_bronze_setup.sql`, adapté de `02_snowflake_setup.sql` (TD 2) : rôle SYSADMIN, warehouse `SIDEFLIX_WH`, `IF NOT EXISTS` partout (relance sans effet, rien n'est écrasé). Il crée dans `SIDEFLIX.BRONZE` :
  - `JSON_LINES` : format de fichier JSON, un objet par ligne (format des fichiers de l'étape 3) ;
  - `SESSIONS_STAGE` : stage interne, zone de dépôt des fichiers JSON avant `COPY INTO` (équivalent de `MERCH_STAGE`) ;
  - `SESSIONS_RAW` : `raw VARIANT`, `_source_file`, `_loaded_at`. Le JSON est stocké tel quel (schema on read) ; doublons et valeurs invalides y restent volontairement, le nettoyage se fait dans Silver (dbt) ;
  - `CATALOG` : colonnes du catalogue PostgreSQL + `_loaded_at`, clé `content_id` ; cible du MERGE incrémental (équivalent de `ORDERS_INCR`) ;
  - `LOAD_RUNS` : journal des exécutions de l'ingestion du catalogue (équivalent de `LOAD_RUNS` du TD 2).
- Exécution dans Snowsight, rôle SYSADMIN choisi dans la feuille, script entièrement sélectionné.
- `ingestion/check_connection.py` : reprend `connect_snowflake()` du TD 2 (paire de clés RSA, variables d'environnement, rôle SYSADMIN). Ne modifie rien : lit le contexte de session et compte les lignes Bronze.
- `ingestion/.env.example` : modèle des trois variables, sans secret. Le vrai `.env` est exclu par `.gitignore`.

## Contrôles effectivement exécutés

| Contrôle | Attendu | Obtenu | Preuve |
| --- | --- | --- | --- |
| Format de fichier | `JSON_LINES`, type JSON, SYSADMIN | conforme | `rendu/snowflake_4_3_bronze_objects.csv` |
| Stage | `SESSIONS_STAGE`, interne, SYSADMIN | `Internal Named`, SYSADMIN | idem |
| Tables Bronze | `CATALOG`, `LOAD_RUNS`, `SESSIONS_RAW`, SYSADMIN, vides | les trois présentes, SYSADMIN, 0 ligne | idem |
| Connexion d'un script sans mot de passe | REDGRAVE_AIRFLOW, SYSADMIN, SIDEFLIX_WH, SIDEFLIX.BRONZE | identique ; 0 ligne dans les trois tables ; code retour 0 | `rendu/python_4_3_check_connection.txt` |
| Clé hors du dépôt | aucun `.p8` ni `.env` dans le projet | clé dans `C:\Users\jerem\redgave\keys\` ; `.env`, `*.p8` exclus par `.gitignore` | contrôle des fichiers |

Le test Python a été lancé deux fois : par Jérémy dans son terminal (sortie identique jusqu'à `CATALOG`, fin de la copie tronquée) puis depuis le même poste avec le même Python 3.11 pour conserver la sortie complète. Le connecteur affiche un avertissement de dépréciation (`FutureWarning` sur `enable_server_session_keep_alive_auto_detection`) sans effet sur le résultat.

## Points à connaître

- Le poste a deux installations de Python : les paquets du TD 2 (`snowflake-connector-python` 5.1.0, `psycopg2-binary` 2.9.13, `cryptography` 48.0.0) sont sur **Python 3.11**, celui du terminal habituel. Rien n'a été installé pour cette action.
- Utilisateur : `REDGRAVE_AIRFLOW` (voir action 4.2 : droits ACCOUNTADMIN plus larges que nécessaire, limite à présenter à l'oral).
- Coût : première utilisation de `SIDEFLIX_WH`, quelques secondes de calcul ; arrêt automatique après 60 s.
- Hors périmètre (étape 5) : dépôt des fichiers sur le stage, `COPY INTO SESSIONS_RAW`, script MERGE du catalogue.

## Reproduction

1. Snowsight : rôle SYSADMIN dans la feuille, coller `ingestion/01_bronze_setup.sql`, tout sélectionner, exécuter ; comparer le tableau final à `rendu/snowflake_4_3_bronze_objects.csv`.
2. PowerShell, dossier `Sideflix` : définir `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PRIVATE_KEY_FILE` (voir `ingestion/.env.example`), puis `python ingestion/check_connection.py`.

## Prochaine action

Étape 5 : 5.1 adapter `incremental_orders.py` en `incremental_catalog.py` (watermark `updated_at`, MERGE sur `content_id`, journal `LOAD_RUNS`) ; 5.3 déposer les fichiers JSON sur `SESSIONS_STAGE` puis `COPY INTO SESSIONS_RAW`.

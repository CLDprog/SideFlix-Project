# Sideflix dbt

Adaptation des TD 3.2 et 3.3. Sources existantes : SIDEFLIX.BRONZE.CATALOG et SESSIONS_RAW.

Le profil fourni est celui de **dbt Projects on Snowflake / Workspaces** (session courante, sans cle ni mot de passe). Il ne convient pas tel quel a dbt Core sur un poste ou dans Docker : y utiliser un profil local avec variables et sa propre cle, comme au TD 3.1/4.2.

Silver : vues reconstruites, Gold : table reconstruite. Le hook log_run_results du TD journalise les executions dans SIDEFLIX.LAB.DBT_RESULTS. Aucune modification des sources Bronze.

Commandes : `dbt run`, puis `dbt docs generate`. Les tests et leur preuve seront completes a l'etape 7, avec `dbt build` puis `dbt source freshness` separement.

Reference du 30 octobre : A = 2 sessions / 45 min ; B = 1 session / 10 min. Ensemble : 32 lignes brutes = 30 sessions valides + 1 rejet + 1 doublon retire.

## Version finale v2 (4 novembre)

Les lots vérifiés sont fixés dans `vars` de `dbt_project.yml`. Les cinq sources publiques alimentent les vues Silver puis `gold_editorial_weekly`, avec périodes, provenance, absence Netflix explicite et simulation signalée. Gold ne lit que Silver. Voir `rendu/Etape_6_V2_Verifications.md` et `gold_editorial_v2.csv`.

Core : installer `dbt/requirements.txt`, charger les variables Snowflake/RSA locales, exporter `SNOWFLAKE_DISABLE_PLATFORM_DETECTION=true AWS_EC2_METADATA_DISABLED=true DBT_SEND_ANONYMOUS_USAGE_STATS=false`, puis depuis la racine : `.venv/bin/dbt run --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core`. Pour Workspaces, utiliser son profil existant. Le profil Core n'embarque aucune clé. Le hook distingue désormais les deux runtimes.

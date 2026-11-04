# Sideflix dbt

Adaptation des TD 3.2 et 3.3. Sources existantes : SIDEFLIX.BRONZE.CATALOG et SESSIONS_RAW.

Le profil fourni est celui de **dbt Projects on Snowflake / Workspaces** (session courante, sans cle ni mot de passe). Il ne convient pas tel quel a dbt Core sur un poste ou dans Docker : y utiliser un profil local avec variables et sa propre cle, comme au TD 3.1/4.2.

Silver : vues reconstruites, Gold : table reconstruite. Le hook log_run_results du TD journalise les executions dans SIDEFLIX.LAB.DBT_RESULTS. Aucune modification des sources Bronze.

Commandes : `dbt run`, puis `dbt docs generate`. Les tests et leur preuve seront completes a l'etape 7, avec `dbt build` puis `dbt source freshness` separement.

Reference du 30 octobre : A = 2 sessions / 45 min ; B = 1 session / 10 min. Ensemble : 32 lignes brutes = 30 sessions valides + 1 rejet + 1 doublon retire.

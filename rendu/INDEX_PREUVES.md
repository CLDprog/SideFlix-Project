# Index des preuves : exigence, fichiers, résultat

4 novembre 2026. Chaque ligne relie une exigence du Framework et du barème aux fichiers du dépôt qui la prouvent. Les rapports `rendu/Etape_*_V2_Verifications.md` détaillent commandes, résultats et limites ; les fichiers bruts sont les sorties réelles, sans secret. Les preuves de l’ancien prototype (fichiers sans « V2 ») restent dans le dépôt interne comme historique et ne font pas partie du rendu.

| Exigence | Où la vérifier | Ce que l’on y voit |
| --- | --- | --- |
| Cinq jeux authentiques, provenance et conditions | `source/sources_manifest.csv`, `docs/sources_and_catalogue.md`, `rendu/Collecte_V2_Verifications.md` | URL, SHA-256, période, grain, conditions par fichier ; snapshots partagés dans le dépôt privé, 19/19 empreintes |
| Correspondances entre sources | `source/content_mapping.csv`, `source/catalog_real.csv` | Jointures par tconst IMDb et QID Wikidata, pas par titre |
| Sessions simulées et résultat attendu | `source/v2/sessions/`, `source/v2/expected_daily_usage.csv` | 32 lignes (30 valides, 1 doublon, 1 durée négative), clairement simulées |
| Méthode 1 : base source + watermark/MERGE (TD 2B) | `ingestion/incremental_catalog.py`, `rendu/Etape_5_V2_Verifications.md`, `rendu/python_5_v2_catalog_initial.txt`, `rendu/python_5_v2_catalog_replay.txt`, `rendu/python_5_v2_catalog_lab.txt` | Premier passage puis rejeu à 0 ; mise à jour testée en LAB |
| Méthode 2 : fichiers, stage, COPY INTO (TD 2A) | `ingestion/load_sessions.py`, `rendu/python_5_v2_sources_initial.txt`, `rendu/python_5_v2_sources_replay.txt` | Rejeu : « 0 files processed », 0 nouvelle ligne |
| Méthode 3 : API, requests, VARIANT (pack 05) | `ingestion/load_sessions.py`, `rendu/ingestion_v2_initial.json`, `rendu/ingestion_v2_replay.json` | Lots identifiés par empreinte, MERGE sur lot et URL |
| Bronze et métadonnées de lot | `ingestion/04_bronze_v2_setup.sql`, `rendu/Etape_4_3_V2_Verifications.md`, `rendu/python_5_v2_reconciliation.txt` | SOURCE_SYSTEM, _BATCH_ID, _source_file, _loaded_at, journal PUBLIC_SOURCE_RUNS |
| Terraform et state partagé | `terraform/`, `rendu/Etape_4_2_V2_Verifications.md`, `rendu/terraform_4_2_v2_migration_gcs.txt`, `rendu/terraform_4_2_plan_after_apply.txt` | Warehouse en code, state GCS privé/versionné/verrouillé, plan code 0 |
| dbt Silver/Gold et lineage | `dbt/sideflix_dbt/`, `dbt/profiles-core/`, `rendu/Etape_6_V2_Verifications.md`, `rendu/dbt_6_v2_run.txt`, `rendu/dbt_6_v2_docs.txt` | 11 modèles ; lineage par dbt docs generate |
| Contrôles qualité et fraîcheur | `dbt/sideflix_dbt/tests/`, `rendu/Etape_7_V2_Verifications.md`, `rendu/dbt_7_v2_build.txt`, `rendu/dbt_7_v2_freshness.txt` | dbt build 33/33 (21 tests), fraîcheur 2/2 |
| Gold vérifié par un calcul indépendant | `ingestion/verify_business_samples.py`, `rendu/dbt_6_v2_business_checks.txt`, `rendu/dbt_7_v2_business_samples.txt`, `rendu/gold_editorial_v2.csv` | 14 lignes contenu/jour identiques à l’attendu ; exemples MovieLens, Wikimedia, Netflix recalculés |
| Docker et Airflow (TD 4.2) | `docker/`, `airflow/`, `rendu/Etape_8_V2_Verifications.md`, `rendu/airflow_8_v2_windows_runs.txt`, `rendu/airflow_8_v2_windows_task_logs.txt`, `rendu/pipeline_8_v2_airflow_publication.txt` | Run du 1er novembre, rejeu, publication unique ; jour sans données bloqué |
| Alerte réelle sur échec | `rendu/airflow_8_4_alerte_slack.txt`, `rendu/slack_8_4_alerte_recue.png`, `rendu/incident_9_1_slack_confirmation.txt` | Message reçu dans #sideflix-alertes |
| Incident 1 : donnée invalide bloquée puis reprise | `rendu/Etape_9_V2_Verifications.md`, `rendu/incident_9_1_failed_and_cleanup.json`, `rendu/incident_9_1_recovery.json`, `rendu/incident_9_1_logs/`, `rendu/incident_9_1_recovery_logs/` | accepted_values en échec, Gold et publication intactes, run correctif 33/33 |
| Incident 2 : crash après écriture, retry idempotent | `rendu/incident_9_2_after_first_write.json`, `rendu/incident_9_2_recovered.json`, `rendu/incident_9_2_logs/` | Une seule ligne par date après retry (MERGE) |
| Fichier manquant et rejeu complet | `rendu/Procedure_9_3_Fichier_Manquant.md`, `rendu/incident_9_4_replay.json`, `rendu/incident_9_4_logs/` | Procédure écrite ; deux runs normaux stables |
| Droits limités et secrets | `governance/`, `rendu/Etape_10_access_tests.txt`, `rendu/Etape_10_admin_outputs.txt`, `rendu/Etape_10_runner_run.txt`, `.gitignore`, `.dockerignore` | 11 contrôles d’accès conformes ; run sous SIDEFLIX_RUNNER sans rôle admin |
| Coûts, budget et performance | `rendu/Etape_10_V2_Verifications.md`, `rendu/Etape_10_Mesures.json`, `rendu/Etape_10_admin_outputs.txt` | 1,44 crédit réel ; ≈ 1,5 crédit/mois projeté ; moniteur 10 crédits ; requête 248 ms, 3/5 partitions |
| Arrêt, reprise, nettoyage | `governance/README.md`, `airflow/README.md` | Pause du DAG, down sans -v, suspension du warehouse, redémarrage |
| Architecture | `docs/architecture_v2.md`, `docs/architecture_v2.png` | Schéma fidèle aux composants exécutés |

## Runs et versions (preuves d’exécution)

| Run Airflow | Poste | Jour traité | Résultat | Preuve |
| --- | --- | --- | --- | --- |
| `scheduled__2026-11-04T05:00:00+00:00` (4/11, 16:05 UTC) | Jérémy | 2026-11-03 | Échec attendu au contrôle des sources après 3 tentatives, rien publié | `rendu/airflow_8_v2_windows_runs.txt` |
| `demo_20261101_run1` (4/11, 16:06 UTC) | Jérémy | 2026-11-01 | Succès : 6 lots sans nouvelle ligne, build 33/33, 13 sessions / 177,4 min publiées | `rendu/airflow_8_v2_windows_task_logs.txt` |
| `demo_20261101_run2_replay` (4/11, 16:09 UTC) | Jérémy | 2026-11-01 | Rejeu : 0 nouvelle ligne, une seule publication | `rendu/pipeline_8_v2_airflow_publication.txt` |
| `alert_test_20261103` (4/11, 16:31 UTC) | Jérémy | 2026-11-03 | Échec réel, alerte reçue sur Slack | `rendu/airflow_8_4_alerte_slack.txt` |
| `matis_9_1_bad_device` puis `matis_9_1_fixed` (4/11) | Matis | 2026-11-01 | Test qualité en échec, Gold protégée, alerte, reprise 33/33 | `rendu/incident_9_1_failed_and_cleanup.json`, `rendu/incident_9_1_recovery.json` |
| `matis_9_2_crash` (4/11) | Matis | 2026-11-01 | Crash après écriture, retry, une ligne par date | `rendu/incident_9_2_recovered.json` |
| `matis_9_replay1`, `matis_9_replay2` (4/11) | Matis | 2026-11-01 | Deux runs normaux stables | `rendu/incident_9_4_replay.json` |
| `runner_normal_20261101` (4/11, 18:13 UTC) | Jérémy | 2026-11-01 | Succès sous SIDEFLIX_RUNNER : 94 requêtes, 0 erreur, build 33/33 | `rendu/Etape_10_runner_run.txt` |

Versions exécutées : Python 3.12.7 (images), Airflow 3.3.2 avec apache-airflow-providers-docker 4.5.9, dbt Core 1.11.16 et dbt-snowflake 1.11.6, snowflake-connector-python 4.8.0, PostgreSQL 16.4, Docker 29.9.2 (poste de Jérémy) et 29.3.1 (poste de Matis), Terraform 1.16.6 avec le provider snowflakedb/snowflake 2.22.1.

Documentation dbt et lineage : `dbt docs generate --static` exécuté sous le rôle SIDEFLIX_RUNNER ; graphe dans `docs/dbt_lineage.png`.

Contributions : Matis Douay (collecte des sources, Bronze v2, ingestion, dbt v2, tests, incidents, préparation de l’étape 10), Jérémy Caillaud (socle Snowflake, Terraform et state GCS, accès du groupe, exécution Docker/Airflow et alerte Slack, intervention administrative et validations de l’étape 10, livrables), Rayan Faher Bonne (couche de consommation : restitution Snowsight depuis Gold avec le rôle analyste en lecture seule, présentée pendant la démonstration). Historique détaillé : `git log` et la roadmap Notion interne.

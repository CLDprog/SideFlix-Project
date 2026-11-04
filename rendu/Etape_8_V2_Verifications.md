# Étape 8 v2 — préparation et blocages

4 novembre 2026, Matis. Étapes 5, 6 et 7 terminées et preuves poussées ; **étape 8 non terminée**.

**Mise à jour du 4 novembre, 17 h 10 (Jérémy)** : exécution réelle dans Docker/Airflow réussie sur le PC de Jérémy (dernière section). 8.1, 8.2, 8.3 et 8.5 validées ; 8.4 reste ouverte jusqu'à la réception d'une alerte sur le webhook Slack du groupe.

## Travail préparé selon TD 4.2 / packs 06 et 07

- `docker/ingestion.Dockerfile`, `docker/dbt.Dockerfile` : base Python 3.12.7 du pack, dépendances fixées, jobs non-root, aucun secret copié, `.dockerignore`.
- `airflow/docker-compose.yml`, `airflow/Dockerfile`, `airflow/dags/sideflix_daily.py` : Airflow standalone/DockerOperator du TD. Ingestion → contrôles → freshness/build → publication. Cron 06 h Paris, deux retries, catchup désactivé, un run à la fois ; date UTC et run_id explicites. Montage RSA en lecture seule, snapshots et reçus de run sur le poste.
- Callback webhook du pack adapté ; URL attendue dans l'environnement privé, jamais dans Git. Réception non testée : webhook du groupe non fourni.
- `ingestion/run_pipeline_job.py` : réutilise collecteur, watermark/MERGE et chargeur existants ; reçu du run transmet les lots vérifiés à dbt. Publication autorisée seulement après build et fraîcheur réussis.
- `ingestion/publish_daily_usage.py` : adaptation du publish_daily_sales du TD ; lit uniquement Gold validée et MERGE par date dans LAB.DAILY_USAGE. Option de crash après écriture préparée pour 9.2, pas déclenchée ici.

Compilation Python et analyse statique Compose réussies ; **cela ne valide pas les images ni le DAG**. Le premier précontrôle local du wrapper dbt a échoué à résoudre l'exécutable (PATH sans `.venv/bin`) ; corrigé par résolution du binaire dans le même environnement Python. La publication sans marqueur de validation a bien été refusée. Les résultats locaux finaux sont consignés dans les fichiers ci-dessous ; ce ne sont pas des preuves Docker/Airflow.

## Résultats locaux obtenus

Ingestion et contrôle des six lots réussis ; APIs réellement rappelées, mêmes empreintes de lot, zéro nouvelle ligne. Freshness puis dbt build à date paramétrée : 33/33 réussis. Publication du 30 octobre exécutée deux fois : 3 sessions /55 minutes et une seule ligne par date à chaque passage. Ces résultats sont obtenus en Python/Core local, pas dans Docker/Airflow. La date éditoriale de référence est ensuite rétablie au 1er novembre.

## Blocages exacts

_Historique : le blocage Docker est levé depuis le 4 novembre à 17 h (exécution sur le PC de Jérémy, dernière section). Le webhook manque toujours._

`docker info` renvoie : `permission denied while trying to connect to the docker API at unix:///Users/matisdouay/.docker/run/docker.sock`.

Il faut un terminal du poste ayant accès à Docker Desktop, puis exécuter la procédure `airflow/README.md`. Ne pas contourner les permissions du socket ou modifier les droits de la clé. Si l'assistant reste restreint, exécuter les commandes Docker dans le terminal du poste et conserver les sorties. Il faut également un webhook Slack/Teams du groupe et une preuve de réception pour terminer 8.4. Aucune intervention ACCOUNTADMIN/Terraform nécessaire à cette étape.

## Preuves / suite

- `docker_8_v2_access.txt` : refus réel du daemon.
- `docker_8_v2_compose_static.txt` : configuration analysée, sans chargement des secrets.
- `pipeline_8_v2_local_ingest.txt`, `pipeline_8_v2_local_check.txt`, `pipeline_8_v2_local_build.txt`, `pipeline_8_v2_local_publish.txt` : précontrôles Python/Core, à distinguer des runs conteneurisés.
- `pipeline_8_v2_restore_reference.txt` : restauration du tableau éditorial à la date de référence versionnée après le test à date paramétrée.

Prochaine action : suivre `airflow/README.md`, construire les images et exécuter un run Airflow puis son rejeu ; contrôler planning/durée/logs, publication unique et réception du webhook. Terminer ensuite les deux incidents 9.1/9.2 avant gouvernance/coûts et remise finale propre. Ne pas annoncer ces étapes achevées.

Échéances communiquées : rendu le 4 novembre, oral le 6 novembre à 13 h Paris. L'heure limite de remise n'a pas pu être vérifiée : aucune URL/session de la plateforme pédagogique identifiée ici ; vérifier sur cette plateforme avant l'envoi final.

## Exécution réelle Docker/Airflow : PC de Jérémy, 4 novembre 2026, 17 h 05 à 17 h 10 (Paris)

Docker Desktop 29.9.2 (moteur Linux) sous Windows, Airflow 3.3.2 standalone du TD, procédure `airflow/README.md`. Le blocage précédent ne venait que de l'accès de l'assistant au daemon Docker sur le poste de Matis.

### Préparation pour que tout poste du groupe puisse lancer le pipeline

- Snapshots `source/real/` partagés dans le dépôt privé (commit 0577f62, Matis). Sous Windows, Git convertissait les fins de ligne : 14 fichiers sur 19 n'avaient plus l'empreinte du manifeste alors que les versions dans Git étaient justes. Ajout de `.gitattributes` (aucune conversion pour les données sources, commit 8cf1f97) ; contrôle : 19/19 empreintes identiques au manifeste.
- Base source : service `source-db` ajouté au Compose (postgres:16.4, méthode de `docker-compose-databases.yml` du pack 04, identifiants de labo jetables, port 5433 limité à localhost) et service ponctuel `catalog-seed` qui exécute le chargeur existant `source/03_load_real_catalog.py` : `CATALOGUE_OK rows=6 distinct_imdb=6 changed=6`. Plus besoin d'un PostgreSQL installé ni d'un mot de passe personnel.
- DAG : `PGPORT` transmis aux jobs et `extra_hosts host.docker.internal` (portabilité hors Docker Desktop).
- Correction du DAG : le premier run manuel échouait au rendu du template (`dag_run.conf.get('date', data_interval_end...)`). La valeur par défaut d'un `get` est évaluée même quand la date est fournie, et un run manuel Airflow 3 n'a pas d'intervalle de données. Remplacé par une condition évaluée seulement si la date manque. Les tentatives 1 et 2 de ce run gardent l'erreur dans leurs journaux ; la tentative 3, après correction, a réussi.

### Résultats (horaires UTC dans les preuves)

| Run | Jour traité | Résultat | Durée | Détail vérifié dans les journaux |
| --- | --- | --- | --- | --- |
| `scheduled__2026-11-04T05:00:00+00:00`, créé automatiquement à la réactivation du DAG (cron 06 h Paris, catchup désactivé) | 2026-11-03 (veille) | échec attendu | 1 min 35 s | Ingestion réussie : catalogue 6 mises à jour sans changement de valeur (horodatages du nouveau conteneur source), 6 lots identiques à l'étape 5, 0 nouvelle ligne. `check_sources` en échec à 3 tentatives (2 retries) : « No simulated sessions for requested UTC day ». `dbt_build` et `publish_daily_usage` en upstream_failed : rien n'est publié. Callback exécuté : « ALERT NOT DELIVERED: missing ALERT_WEBHOOK_URL ». |
| `demo_20261101_run1`, manuel `{"date":"2026-11-01"}` | 2026-11-01 | succès | 1 min 04 s (tentative réussie) | 6 lots, mêmes batch_id qu'à l'étape 5, 0 nouvelle ligne ; catalogue 0 extraction ; `SOURCE_CHECKS_PASS` ; freshness 2/2 ; `dbt build` PASS=33 WARN=0 ERROR=0 ; `MERGE_PUBLISHED 2026-11-01 13 177.400000`. |
| `demo_20261101_run2_replay`, même date | 2026-11-01 | succès | 1 min 01 s | Mêmes contrôles, 0 nouvelle ligne, build 33/33, publication mise à jour sur la même ligne. |

Contrôle Snowflake indépendant après les runs : `SIDEFLIX.LAB.DAILY_USAGE` contient une seule ligne pour le 2026-11-01 (13 sessions, 177,4 minutes, run_id du rejeu) et aucune date en double. Valeur attendue calculée indépendamment (`source/v2/expected_daily_usage.csv`) : 13 sessions, 177,4 minutes. Volumes Bronze inchangés.

Échéance de 07 h : un run complet dure environ 1 minute pour un déclenchement à 06 h Paris. Mesure locale sur une seule journée simulée, sans contention.

### Statut des sous-étapes

- 8.1 images testées : `sideflix-ingest:1.0.0` et `sideflix-dbt:1.0.0` construites et exécutées par Airflow, jobs non-root.
- 8.2 Airflow démarré avec le Compose du TD, `list-import-errors` : aucune erreur.
- 8.3 dépendances ingest, check, build puis publish respectées ; le contrôle bloque la suite en cas d'échec.
- 8.5 publication par MERGE : une ligne par date après rejeu.
- 8.4 planning (cron 06 h Europe/Paris, catchup désactivé, un run à la fois), retries (3 tentatives observées) et journaux prouvés. **Reste ouverte** : réception réelle d'une alerte sur le webhook Slack du groupe.

### Limites

Sur ce poste, les jobs utilisent l'utilisateur de service Snowflake existant de Jérémy (`REDGRAVE_AIRFLOW`, rôle SYSADMIN imposé par les scripts) ; un utilisateur dédié à moindre privilège relève de l'étape 10. Le conteneur Airflow tourne en root (exception du TD pour le socket Docker). Les sessions simulées s'arrêtent au 1er novembre : un run planifié pour une autre journée échoue volontairement. Effet de bord constaté : à chaque run, le collecteur réécrit les horodatages de contrôle de `source/sources_manifest.csv` et `source/catalog_real.csv` dans le dépôt monté (empreintes inchangées, 19/19). Ces fichiers ont été remis à la version du dépôt après vérification ; à terme, écrire ces horodatages dans `airflow/work` éviterait de modifier des fichiers suivis par Git.

### Preuves

- `airflow_8_v2_windows_runs.txt` : versions, images, services Compose, absence d'erreur d'import, planification, états et horaires des tâches des trois runs.
- `airflow_8_v2_windows_task_logs.txt` : extraits des journaux de chaque tentative (erreur de template corrigée, lots, contrôles, build, publication, callback).
- `pipeline_8_v2_airflow_publication.txt` : contrôle Snowflake en lecture seule après les runs.


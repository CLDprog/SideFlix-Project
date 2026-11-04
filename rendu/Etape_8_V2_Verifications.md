# Étape 8 v2 — préparation et blocages

4 novembre 2026, Matis. Étapes 5, 6 et 7 terminées et preuves poussées ; **étape 8 non terminée**.

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

`docker info` renvoie : `permission denied while trying to connect to the docker API at unix:///Users/matisdouay/.docker/run/docker.sock`.

Il faut un terminal du poste ayant accès à Docker Desktop, puis exécuter la procédure `airflow/README.md`. Ne pas contourner les permissions du socket ou modifier les droits de la clé. Si l'assistant reste restreint, exécuter les commandes Docker dans le terminal du poste et conserver les sorties. Il faut également un webhook Slack/Teams du groupe et une preuve de réception pour terminer 8.4. Aucune intervention ACCOUNTADMIN/Terraform nécessaire à cette étape.

## Preuves / suite

- `docker_8_v2_access.txt` : refus réel du daemon.
- `docker_8_v2_compose_static.txt` : configuration analysée, sans chargement des secrets.
- `pipeline_8_v2_local_ingest.txt`, `pipeline_8_v2_local_check.txt`, `pipeline_8_v2_local_build.txt`, `pipeline_8_v2_local_publish.txt` : précontrôles Python/Core, à distinguer des runs conteneurisés.
- `pipeline_8_v2_restore_reference.txt` : restauration du tableau éditorial à la date de référence versionnée après le test à date paramétrée.

Prochaine action : suivre `airflow/README.md`, construire les images et exécuter un run Airflow puis son rejeu ; contrôler planning/durée/logs, publication unique et réception du webhook. Terminer ensuite les deux incidents 9.1/9.2 avant gouvernance/coûts et remise finale propre. Ne pas annoncer ces étapes achevées.

Échéances communiquées : rendu le 4 novembre, oral le 6 novembre à 13 h Paris. L'heure limite de remise n'a pas pu être vérifiée : aucune URL/session de la plateforme pédagogique identifiée ici ; vérifier sur cette plateforme avant l'envoi final.

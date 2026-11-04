# Étape 8 — lancement selon le TD 4.2

**État : préparée, pas validée dans Docker/Airflow.** L'API Docker est refusée à cette session (`rendu/docker_8_v2_access.txt`). Les étapes 5–7 cloud/Core sont terminées ; ne pas les refaire. Aucun Terraform nécessaire.

## Sur le poste de démonstration

1. Ouvrir Docker Desktop et exécuter `docker info` dans le terminal du poste. Si seul l'assistant est bloqué, exécuter les commandes Docker depuis ce terminal.
2. Depuis la racine du dépôt, préparer les dossiers et le fichier privé :

```sh
mkdir -p airflow/work airflow/state
cp airflow/.env.example airflow/.env
id -u
id -g
```

Renseigner `.env` : compte/utilisateur Snowflake, chemins ABSOLUS de la clé existante, du dépôt et de `airflow/work`, variables PG* du PostgreSQL local et `SIDEFLIX_TASK_USER=UID:GID` retournés ci-dessus. La clé `rsa_key.p8` reste hors Git et est montée en lecture seule. Ne pas changer ses permissions pour rendre le montage accessible : utiliser le bon UID. `PGHOST=host.docker.internal` sur Docker Desktop.

Renseigner un **webhook Slack/Teams du groupe** dans `ALERT_WEBHOOK_URL`. Aucune notification ne sera validée tant que le groupe n'aura pas confirmé sa réception. Le callback vient du pack 07 ; une simple ligne de log sans webhook n'est pas une preuve.

3. Construire et démarrer, depuis la racine :

```sh
docker build -f docker/ingestion.Dockerfile -t sideflix-ingest:1.0.0 .
docker build -f docker/dbt.Dockerfile -t sideflix-dbt:1.0.0 .
docker compose -f airflow/docker-compose.yml up -d --build
docker compose -f airflow/docker-compose.yml exec airflow airflow dags list-import-errors
```

Ouvrir http://localhost:8080. Déclencher `sideflix_daily` avec la configuration **`{"date":"2026-11-01"}`**, puis rejouer la même date. Conserver logs, durée, états des tâches, contrôles de publication et copie sans secret des résultats. Ne pas marquer 8.1–8.4 terminées sur la seule base de la compilation Python ou de `compose config`.

Le DAG reprend DockerOperator/Compose du TD : ingestion réelle (catalogue + cinq sources + sessions), contrôle des lots/date, freshness puis dbt build, publication MERGE. Date UTC et run_id transmis à chaque tâche. Cron 06 h Europe/Paris, retries=2, catchup=False, max_active_runs=1. Airflow est l'unique ordonnanceur. Les jobs sont non-root ; le conteneur Airflow utilise l'exception root du TD pour le socket Docker, exposé seulement sur localhost.

## Démonstration et limites

Les snapshots sont historiques, les sessions simulées s'arrêtent au 1er novembre. Un run automatique demandant une journée absente **échoue** ; aucune donnée du jour n'est inventée. Pour l'oral, spécifier la date ci-dessus. L'image ingestion réutilise les snapshots locaux montés depuis `source/` ; les APIs sont réellement appelées et le reçu du run transmet leurs nouveaux batch_id à dbt sans modifier les variables de référence versionnées.

Le script `run_pipeline_job.py build` écrit un marqueur local seulement après réussite de freshness ET build. `publish_daily_usage.py` exige ce marqueur (date/run/invocation correspondants), lit Gold et fait un MERGE par date dans SIDEFLIX.LAB.DAILY_USAGE. Il refuse une journée absente. La cible du fixture ancien reste distincte ; ne pas y mélanger les tests v2.

Après validation de l'étape 8, poursuivre 9.1 (device invalide → test bloqué → notification → correction) et 9.2 (`--crash-on-try 1` après MERGE, retry → une ligne par date). Ces incidents ne sont pas encore déclarés exécutés. Conserver le dernier Gold valide en cas d'échec amont. Vérifier l'heure de disponibilité 07 h avec un run chronométré ; les seuils freshness seuls ne la prouvent pas.

Arrêt local : `docker compose -f airflow/docker-compose.yml down`. Le compte Snowflake est un essai ; ne pas recréer les objets Terraform ni modifier REDGRAVE.

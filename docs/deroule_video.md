# Déroulé de la vidéo du pipeline (environ 3 minutes)

Poste retenu : Mac de Matis, Docker Desktop. Enregistrement : Maj + Cmd + 5, enregistrer une zone sélectionnée ; microphone si commentaire oral. Variante Windows : Outil Capture d’écran (Win + Maj + R) ou OBS. Ne jamais afficher `airflow/.env`, une clé, l’URL du webhook ni un mot de passe.

## Avant d’enregistrer

1. Confirmer qu’un seul Airflow fonctionne (celui de Jérémy arrêté). Depuis la racine : `git pull --ff-only`, reconstruire les deux images avec les commandes du README, vérifier `SNOWFLAKE_ROLE=SIDEFLIX_RUNNER` dans le `.env` privé, puis `docker compose -f airflow/docker-compose.yml up -d --build`. Le compte de Matis garde sa propre clé ; ne pas copier celle du service de Jérémy. Attendre `list-import-errors` sans erreur.
2. Onglets prêts : Airflow (http://localhost:8080), Snowsight avec une feuille contenant les trois requêtes de vérification du README, Slack sur `#sideflix-alertes`, le dépôt ouvert dans l’explorateur ou VS Code.
3. Choisir un run_id neuf, par exemple `video_matis_20261101_v1`, sans paramètre incident. Ne pas déclencher bad_device. Dans Snowsight : rôle SIDEFLIX_RUNNER et `USE SECONDARY ROLES NONE;` pour les vérifications incluant LAB.DAILY_USAGE ; l’analyste de Rayan ne peut lire que Gold. Fermer les fichiers privés avant l’enregistrement.

## Scènes

| Durée | Écran | À montrer et à dire |
| --- | --- | --- |
| 0:00 à 0:20 | Dépôt | `source/sources_manifest.csv` et `source/real/` : cinq jeux réels avec empreinte et conditions ; `source/v2/sessions/` : sessions **simulées**. |
| 0:20 à 0:50 | Airflow | Graphe de `sideflix_daily` (ingest, check, dbt build, publish), planning 06 h Paris, 2 retries. Déclencher avec la configuration `{"date":"2026-11-01"}`. |
| 0:50 à 1:40 | Airflow | Les quatre tâches passent au vert (couper l’attente au montage si besoin). Ouvrir le journal d’`ingest_sources` : six lots, 0 nouvelle ligne ; celui de `dbt_build` : PASS=33. Montrer brièvement `docs/dbt_lineage.png` pour le lineage. |
| 1:40 à 2:20 | Snowsight | Requête 1 : 13 sessions et 177,4 minutes pour le 1er novembre. Requête 2 : une seule ligne par date dans `LAB.DAILY_USAGE`. Requête 3 : classement éditorial, Whiplash en tête, colonnes de contexte réel et `SIDEFLIX_SESSIONS_SIMULATED = TRUE`. |
| 2:20 à 2:45 | Slack et dépôt | Message d’alerte reçu lors d’un échec réel ; `rendu/Etape_9_V2_Verifications.md` : les deux incidents et leur reprise. |
| 2:45 à 3:00 | Schéma | `docs/architecture_v2.png` : récapitulatif de la chaîne et des rôles limités. |

## Après

Arrêter l’enregistrement, vérifier image/son, ouverture du fichier et absence de secrets, puis l’ajouter aux livrables sous un nom explicite (par exemple Sideflix_pipeline.mp4). Ne pas déclarer la vidéo faite avant de disposer du fichier vérifié et du lien ou dépôt accessible au jury. Sur Mac, Maj + Cmd + 5 permet aussi de choisir le dossier de sauvegarde. Pour arrêter le pipeline : `docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags pause sideflix_daily` puis `docker compose -f airflow/docker-compose.yml down` (sans `-v`).

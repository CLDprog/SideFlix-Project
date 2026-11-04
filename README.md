# Sideflix : un pipeline de données pour un streaming indépendant

Projet « Oral Defense » du cours Data Engineering & Cloud Infrastructure, Albert School, groupe 6 : Matis Douay, Jérémy Caillaud, Rayan Faher Bonne. Oral le 6 novembre 2026.

## Le besoin

Sideflix est une plateforme de streaming **fictive**, inspirée de Netflix réel et spécialisée dans le cinéma indépendant (hypothèses : 10 000 abonnés à 7,99 € par mois, 100 contenus, 6 salariés ; revente à Netflix envisagée comme porte de sortie du scénario).

- **Utilisateur** : le responsable du catalogue.
- **Décision** : quels contenus mettre en avant cette semaine.
- **Rythme** : calcul chaque jour à 06 h (Paris), chiffres disponibles avant 07 h.
- **Grain** : contenu × jour UTC de début de session.
- **Indicateurs** : sessions valides distinctes et minutes regardées (somme des secondes / 60), classement sur sept jours, avec le contexte réel des sources externes affiché à côté et jamais mélangé au rang.

## Architecture exécutée

![Architecture Sideflix](docs/architecture_v2.png)

| Brique | Rôle | Méthode du cours |
| --- | --- | --- |
| PostgreSQL (`source-db`, conteneur) | Base « sur site » du catalogue | Pack 04 |
| `ingestion/incremental_catalog.py` | Catalogue vers Bronze par watermark + MERGE | TD 2, partie B |
| `ingestion/load_sessions.py` | Fichiers et sessions par PUT, stage, COPY INTO ; API par requests vers VARIANT | TD 2, partie A ; pack 05 |
| Snowflake (AWS eu-west-3) | Bronze, Silver, Gold ; warehouse SIDEFLIX_WH X-Small | TD 2, 3.2, 3.3 |
| dbt (`dbt/sideflix_dbt`) | 9 vues Silver (quarantaine, dédoublonnage), 2 tables Gold, 21 tests | TD 3.2, 3.3 ; pack 03 et 07 |
| Docker + Airflow (`docker/`, `airflow/`) | DAG `sideflix_daily` : ingest, check, dbt build, publish ; alerte Slack | TD 4.2 ; pack 06 et 07 |
| Terraform (`terraform/`) | Warehouse SIDEFLIX_WH ; state sur un bucket GCS privé, versionné, verrouillé | TD 4.2 ; pack 09 |
| `governance/` | Rôles SIDEFLIX_ANALYST et SIDEFLIX_RUNNER, utilisateur de service, moniteur de budget | TD 2 |

Détails : [docs/architecture_v2.md](docs/architecture_v2.md).

## Les données

Cinq jeux **authentiques**, chacun avec URL, empreinte SHA-256, période, grain et conditions d’usage dans [`source/sources_manifest.csv`](source/sources_manifest.csv) ; détails dans [docs/sources_and_catalogue.md](docs/sources_and_catalogue.md).

| Jeu | Usage | Période |
| --- | --- | --- |
| IMDb | Titre, type, année, durée des six œuvres | Snapshot du 4/11/2026 |
| MovieLens | 74 notes : moyenne et nombre par œuvre | 1996 à 2018 |
| Netflix Top 10 | Rangs hebdomadaires ; un appariement certain (Sicario) | Semaine du 9/03/2025 |
| Wikidata | Identité (QID), liens IMDb et Wikipédia | Réponse du 4/11/2026 |
| Wikimedia | Consultations Wikipédia par jour (42 observations) | 26/10 au 1/11/2026 |

Les **sessions Sideflix sont simulées** (`source/v2/sessions/`, 32 lignes sur trois jours) et ne comptent pas parmi les cinq jeux. Le résultat attendu, calculé indépendamment, est dans `source/v2/expected_daily_usage.csv`. Les snapshots bruts (`source/real/`) sont partagés pour un usage interne au groupe : la copie publique éventuelle doit exclure les exports IMDb et Netflix, dont les conditions n’autorisent pas la redistribution.

## Lancer le pipeline

Prérequis : Docker Desktop, Python 3.11 ou plus, un compte Snowflake avec une paire de clés RSA par utilisateur (`gen_key.py` du TD 2), un webhook Slack (Incoming Webhook) pour les alertes, Terraform 1.9 ou plus et un accès au bucket GCS du state pour toute opération Terraform.

1. **Objets Snowflake** (une seule fois) : `ingestion/00_create_sideflix_objects.sql` (base et schémas, rôle SYSADMIN), `terraform init` puis `terraform plan` dans `terraform/` (warehouse ; voir `terraform/README.md`), `ingestion/01_bronze_setup.sql` puis `ingestion/04_bronze_v2_setup.sql` (Bronze), et en ACCOUNTADMIN `governance/10_admin_setup.sql` puis `governance/10b_pipeline_user.sql` (rôles, moniteur, utilisateur de service).
2. **Configuration privée** : copier `airflow/.env.example` en `airflow/.env` et renseigner le compte, l’utilisateur (`SIDEFLIX_PIPELINE`), le dossier de sa clé, les chemins absolus du dépôt et de `airflow/work`, et l’URL du webhook. Ce fichier n’est jamais versionné.
3. **Images et services** :

```sh
docker build -f docker/ingestion.Dockerfile -t sideflix-ingest:1.0.0 .
docker build -f docker/dbt.Dockerfile -t sideflix-dbt:1.0.0 .
docker compose -f airflow/docker-compose.yml up -d --build
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags list-import-errors
```

4. **Run de démonstration** : dans http://localhost:8080, activer `sideflix_daily` et le déclencher avec la configuration `{"date":"2026-11-01"}` (ou `airflow dags trigger sideflix_daily --conf '{"date":"2026-11-01"}'` via `/entrypoint`). Les sessions simulées couvrent le 30 octobre au 1er novembre : un run planifié pour un autre jour échoue volontairement au contrôle des sources, sans rien publier.
5. **Vérifier** dans Snowsight :

```sql
SELECT usage_date, SUM(valid_sessions) AS sessions, SUM(minutes_watched) AS minutes
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY WHERE usage_date = '2026-11-01' GROUP BY 1;   -- 13 sessions, 177,4 minutes
SELECT * FROM SIDEFLIX.LAB.DAILY_USAGE ORDER BY usage_date;                        -- une ligne par date
SELECT * FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY ORDER BY editorial_rank;          -- classement et contexte
```

Le lineage se génère avec `dbt docs generate --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core` ; graphe : [docs/dbt_lineage.png](docs/dbt_lineage.png). Arrêt, reprise et nettoyage : [governance/README.md](governance/README.md).

## Résultats et fiabilité

- **Classement au 1er novembre** : Whiplash en tête (7 sessions, 112,7 minutes), devant Moonlight, Sicario, Frances Ha, Room et Get Out. Les 14 lignes contenu/jour sont identiques au calcul indépendant.
- **Qualité** : `dbt build` 33/33 (11 modèles, 21 tests), fraîcheur 2/2, réconciliation 32 = 30 valides + 1 quarantaine + 1 doublon.
- **Rejeu** : relancer la même date n’ajoute aucune ligne et laisse une seule publication par date.
- **Incident 1** : une valeur `device` invalide (copie isolée) fait échouer le test, bloque Gold et la publication, déclenche l’alerte Slack ; reprise par retrait du seul lot de test.
- **Incident 2** : un crash après écriture est rattrapé par le retry ; le MERGE garde une seule ligne par date.
- **Sécurité** : pipeline exécuté par l’utilisateur de service `SIDEFLIX_PIPELINE` avec le seul rôle `SIDEFLIX_RUNNER` ; le rôle analyste lit Gold et rien d’autre ; aucun secret dans Git ni dans les images.
- **Coûts** : 1,44 crédit réellement consommé (développement et tests compris) ; environ 1,5 crédit par mois projeté pour un run quotidien ; moniteur de 10 crédits par mois (alertes à 50 et 80 %, arrêt à 100 %).

Toutes les preuves : [rendu/INDEX_PREUVES.md](rendu/INDEX_PREUVES.md).

## Étapes manuelles et limites

- Manuelles : compte Snowflake et clé RSA par utilisateur, webhook Slack, bucket GCS du state, activation des notifications e-mail du moniteur dans Snowsight.
- Limites : sessions simulées sur trois jours ; sources externes historiques ou datées ; un seul appariement Netflix ; deux fournisseurs cloud (AWS pour Snowflake, GCS pour le seul state Terraform) ; compte Snowflake d’essai.

## Contributions

Voir la fin de [rendu/INDEX_PREUVES.md](rendu/INDEX_PREUVES.md) et l’historique Git. Journal de travail interne : [docs/journal_interne.md](docs/journal_interne.md).

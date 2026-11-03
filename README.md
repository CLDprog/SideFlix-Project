# Sideflix — projet scolaire

Pipeline analytique d’une plateforme fictive de streaming indépendant, réalisé avec les méthodes des cours et TD de Data Engineering & Cloud Infrastructure.

## Cadrage retenu

Entreprise fictive : 10 000 abonnés à 7,99 €/mois, 100 contenus et 6 salariés. Ces hypothèses sont distinctes du petit jeu de démonstration.

Besoin : aider le responsable du catalogue à préparer les mises en avant de la semaine. Calcul quotidien à 6 h, heure de Paris, disponible avant 7 h.

- Sessions valides distinctes par contenu et par jour UTC.
- Minutes visionnées : somme des secondes valides divisée par 60.
- Classement sur sept jours selon les minutes visionnées.

Une session est un résumé final de lecture. Une ligne par session après dédoublonnage ; le jour est celui du début de la session en UTC. Un épisode de série est un contenu. Toutes les données sont fictives.

## Architecture prévue

Catalogue PostgreSQL (watermark + MERGE, TD 2) et sessions JSON (stage + COPY INTO, TD 3.3), puis Bronze → Silver dbt → Gold dbt dans Snowflake. Restitution SQL dans Snowsight. Docker exécutera les jobs, Airflow les ordonnera et Terraform créera le warehouse.

PostgreSQL et le pilotage restent locaux ; stockage et calculs analytiques seront dans Snowflake. Les objets REDGRAVE des TD sont conservés.

## Dossiers

| Dossier | Rôle |
| --- | --- |
| `source/` | SQL du catalogue et fichiers de sessions |
| `ingestion/` | `00_create_sideflix_objects.sql` (base et schémas, 4.1), `01_bronze_setup.sql` (format JSON, stage, tables Bronze, 4.3), `check_connection.py` et `.env.example` (connexion par clé, 4.3), `incremental_catalog.py` (catalogue, watermark + MERGE), `load_sessions.py` (sessions, PUT + COPY INTO), `02_check_bronze.sql` (contrôle Bronze), `03_create_team_users.sql` (accès Snowflake de Matis et Rayan, sans mot de passe dans le fichier) |
| `dbt/` | À compléter aux étapes 6 et 7 |
| `airflow/` | À compléter à l’étape 8 |
| `terraform/` | Warehouse `SIDEFLIX_WH` déclaré en IaC (module du TD 4.2) ; `terraform.tfvars` et state locaux, non versionnés |
| `rendu/` | Contrôles, preuves et futurs documents de rendu |

## Préparer le catalogue sur son poste

Prérequis : PostgreSQL 16 démarré et outils `createdb`/`psql` disponibles. Depuis ce dossier, avec son utilisateur PostgreSQL local :

```sh
createdb -h 127.0.0.1 sideflix
psql -X -h 127.0.0.1 -v ON_ERROR_STOP=1 -d sideflix -f source/01_create_catalog.sql
```

Si la base existe déjà, ignorer uniquement `createdb`. Le SQL conserve les contenus existants et ne réinitialise pas les titres modifiés. Il attend un compte local autorisé à créer la table et son trigger ; utiliser ses propres paramètres de connexion si nécessaire.

La table `public.catalog` contient 6 contenus (A à F), une clé primaire, une durée strictement positive et un trigger mettant `updated_at` à jour à chaque modification, comme au TD 2.

## Sessions de démonstration

`source/sessions/` contient trois fichiers JSON **avec un objet par ligne** (pas de tableau englobant). Ils seront chargés dans une colonne VARIANT à l’étape 5.

Champs : `session_id`, `content_id`, `viewer_id`, `started_at`, `watched_seconds`, `device`. Dates UTC, durées en secondes, identifiants de spectateurs fictifs. Appareils autorisés : `web`, `mobile`, `tv`.

| Jour UTC | Lignes brutes | Sessions valides distinctes | Cas volontaire |
| --- | --- | --- | --- |
| 2026-10-30 | 3 | 3 | Référence manuelle du PDF |
| 2026-10-31 | 15 | 14 | Doublon exact de S4 |
| 2026-11-01 | 14 | 13 | S31 : durée de -60 secondes |
| Total | 32 | 30 | 1 doublon et 1 rejet attendu |

Référence du 30 octobre : S1/A = 1 800 s ; S2/A = 900 s ; S3/B = 600 s. Après transformation : A = 2 sessions / 45 minutes ; B = 1 session / 10 minutes ; total = 3 sessions / 55 minutes. Aucun autre visionnage ce jour-là.

Les anomalies sont conservées dans les fichiers bruts pour démontrer la quarantaine et le dédoublonnage plus tard. Les résultats ci-dessus sont attendus ; ils ne prouvent pas encore une exécution dans Snowflake.

## Travail à plusieurs

[Projet et roadmap Notion](https://app.notion.com/p/40cf4ba8c522812db500d27d4f5662c4).

Consulter l’avancement, choisir une tâche disponible, indiquer sa prise en charge, puis noter les fichiers, contrôles, résultats et prochaine action en fin de session. Pas de rôle fixe A/B/C. Les contributions de chacun restent identifiables pour l’oral.

Le dépôt est initialisé localement ; sa publication sur GitHub reste à faire pour partager le code. Les fichiers et preuves sont regroupés ici ; Notion suit les tâches.

## Références

- `Sideflix_Plan_Action_Scolaire.pdf`, étapes 3 et 7.
- TD 2 : `01_create_merch_db.sql` (table, contraintes, trigger).
- TD 3.3 : option fichiers JSON (ingestion à réaliser).

## État du travail

Voir `rendu/Etape_3_Verifications.md` (sources) et `rendu/Etape_4_1_Verifications.md` (base `SIDEFLIX` et schémas BRONZE, SILVER, GOLD, LAB créés par SYSADMIN ; compte Snowflake sur AWS, région `AWS_EU_WEST_3`). `rendu/Etape_4_2_Verifications.md` : warehouse `SIDEFLIX_WH` (X-Small, auto-suspend 60 s) créé par Terraform, second plan sans changement. `rendu/Etape_4_3_Verifications.md` : format JSON, stage interne et tables Bronze vides créés ; connexion d’un script par paire de clés vérifiée. `rendu/Etape_5_Verifications.md` : les deux sources sont chargées en Bronze (6 contenus, 32 lignes de sessions), replay et mise à jour vérifiés, 10 contrôles OK. dbt (étapes 6-7) et orchestration restent à réaliser.

Ne jamais versionner les clés, mots de passe, fichiers `.env` ou états Terraform.

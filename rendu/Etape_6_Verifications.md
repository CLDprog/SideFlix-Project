# Étape 6 — modèles dbt, 4 novembre 2026

Session de Matis, avec assistance de l’IA. Références : plan scolaire, étapes 6 et 7 ; projets dbt des TD 3.2 et 3.3.

## Réalisé dans Snowflake

Compte du groupe : `tozpkte/ml45551`, utilisateur `MATIS_DOUAY`, rôle `SYSADMIN`, warehouse `SIDEFLIX_WH`.

Espace privé de Matis **Sideflix_dbt**, projet **sideflix_dbt**, profil dev. La session Snowflake est utilisée comme au TD 3.2 ; aucun mot de passe ni clé dans les fichiers. Les objets de Jérémy sont réutilisés.

Code conservé sous `dbt/sideflix_dbt/`. Importer ce dossier avec « Add new > Upload folder » dans Workspaces, puis sélectionner le projet et le profil dev. La configuration des schémas et le hook de journalisation reprennent les macros du TD 3.2. Les deux modèles d’exemple créés automatiquement par Snowflake sont désactivés ; seuls les cinq modèles Sideflix s’exécutent.

| Modèle | Rôle | Objet créé |
| --- | --- | --- |
| silver_catalog | Nettoyage du titre/type, typage et conservation des dates | SIDEFLIX.SILVER.SILVER_CATALOG (vue) |
| stg_sessions | Lecture JSON avec TRY_, conversion UTC, provenance | SIDEFLIX.SILVER.STG_SESSIONS (vue) |
| quarantine_sessions | Conservation des lignes invalides avec motif | SIDEFLIX.SILVER.QUARANTINE_SESSIONS (vue) |
| silver_sessions | Jointure au catalogue, règles de validité, ROW_NUMBER / QUALIFY | SIDEFLIX.SILVER.SILVER_SESSIONS (vue) |
| gold_content_daily | Sessions distinctes et somme des secondes / 60 par jour UTC et contenu | SIDEFLIX.GOLD.GOLD_CONTENT_DAILY (table) |

Les vues et la table sont recalculées ; aucune transformation incrémentale supplémentaire. Le champ device n’est pas filtré en Silver pour permettre le futur test accepted_values en échec. Les modèles ne modifient pas Bronze.

## Exécutions et résultats observés

`dbt run --target dev` a terminé avec succès : dbt 1.9.4 / adapter Snowflake 1.9.2, 5 modèles et 1 hook, PASS=6 WARN=0 ERROR=0 SKIP=0 TOTAL=6. Il s’agit des modèles et du hook, pas de six tests qualité. Le hook écrit les résultats dans SIDEFLIX.LAB.DBT_RESULTS.

`dbt docs generate --target dev` a terminé, avec « Catalog written to /tmp/dbt/target/catalog.json ». Descriptions et dépendances sont dans les YAML et les appels source()/ref().

Contrôle SQL effectivement exécuté dans ce même compte :

| Contrôle | Résultat |
| --- | --- |
| Catalogue Bronze / Silver | 6 / 6 |
| Sessions Bronze / staging | 32 / 32 |
| Quarantaine | 1 ligne, S31, invalid_watched_seconds |
| Sessions Silver | 30 sessions valides distinctes |
| A, 30 octobre | 2 sessions / 45 minutes |
| B, 30 octobre | 1 session / 10 minutes |

Le classement sur sept jours (du 26 octobre au 1er novembre inclus) a été exécuté : A arrive en tête avec 7 sessions et 112,666667 minutes, puis B, E, C, D et F. Le titre de B reste la version restaurée modifiée par Jérémy. La date de démonstration est fixe ; les seules journées du jeu sont les 30 et 31 octobre et le 1er novembre.

## Preuves et reproduction

- `snowflake_6_0_bronze.csv` : export CSV réel des volumes et colonnes avant transformation.
- `dbt_6_execution_extraits.txt` : extraits des sorties run et docs observées dans Workspaces.
- `snowflake_6_resultats.tsv` : neuf résultats copiés depuis la grille Snowflake.
- `snowflake_6_classement.tsv` : transcription des six lignes du classement affiché.
- `06_check_results.sql` : contrôles et requête de classement, en lecture seule.

Accès au workspace de Matis : https://app.snowflake.com/tozpkte/ml45551/#/workspaces/ws/USER%24/PUBLIC/Sideflix_dbt

L’espace est privé à Matis ; les vues Silver et la table Gold sont dans la base du groupe. Les autres membres récupèrent les fichiers joints dans Notion pour reproduire le projet dans leur espace ou poursuivre le code.

## Passation et limites

Étape 6 réalisée et vérifiée. **Étape suivante : 7**, ajouter les tests dbt et de réconciliation, lancer dbt build et dbt source freshness séparément, puis vérifier la complétude et conserver les preuves. Les résultats métier sont déjà contrôlés ; cela ne remplace pas ces tests.

Le dépôt GitHub privé du groupe reste inaccessible depuis le connecteur et le client GitHub du poste : ces nouveaux fichiers ne sont donc pas publiés dans le dépôt de Jérémy. Archive jointe dans Notion pour intégration. Elle contient uniquement le projet dbt et les nouvelles preuves ; copier son contenu dans la racine du projet possédant déjà ingestion/, source/, dbt/ et rendu/, après avoir récupéré la version du groupe. Ne pas remplacer les fichiers d’ingestion, le README du groupe ni le state Terraform.

Le profil fourni est réservé à dbt Projects on Snowflake. Pour Docker/Airflow à l’étape 8, adapter un profil dbt Core avec variables et clé comme au TD 3.1/4.2 ; ne pas utiliser les valeurs « not needed » en local.

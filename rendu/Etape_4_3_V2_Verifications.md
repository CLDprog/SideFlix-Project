# Étape 4.3 v2 — exécutée et vérifiée dans Snowflake

Compte du groupe tozpkte/ml45551 ; session MATIS_DOUAY, rôle SYSADMIN, warehouse SIDEFLIX_WH. SQL adapté du setup des TD : ingestion/04_bronze_v2_setup.sql. Aucun DROP ni remplacement des données du prototype.

Créations/compléments : IMDB_RAW, MOVIELENS_RAW, NETFLIX_RAW, WIKIDATA_RAW, WIKIMEDIA_RAW ; raw VARIANT, fichier, horodatage, batch et source. CATALOG enrichi de l’identifiant IMDb et de la provenance ; SESSIONS_RAW enrichie de la source/batch. Stage PUBLIC_SOURCES_STAGE, formats CSV/TSV et journal PUBLIC_SOURCE_RUNS préparés. Copies de référence catalogue/sessions/Gold conservées dans LAB.

Rejeu du script validé avec les colonnes ajoutées sans redéfinir leurs valeurs par défaut ; copies de référence conservées. Vérification réelle par ingestion/04b_check_bronze_v2_setup.sql : export rendu/Etape_4_3_V2_Resultats.csv, sept contrôles OK :

| Contrôle | Obtenu | Attendu |
| --- | --- | --- |
| Tables des cinq sources réelles | 5 | 5 |
| Colonnes brutes/métadonnées | 25 | 25 |
| Métadonnées catalogue | 5 | 5 |
| Métadonnées sessions | 5 | 5 |
| Catalogue de référence conservé | 6 | 6 |
| Sessions brutes de référence conservées | 32 | 32 |
| Minutes de référence du 30 octobre | 55 | 55 |

Les cinq nouveaux jeux ne sont pas encore chargés : étape 5 non commencée. La création des objets ne prouve pas leur ingestion ni la validation des modèles dbt v2.

## Étape 4 encore ouverte

Le warehouse Terraform existant est conservé. L’exigence de state d’équipe inscrite en 4.2 n’est pas encore vérifiée : le state actuel est uniquement sur le poste de Jérémy. Exemple S3 et procédure préparés dans terraform/backend.tf.example et terraform/README.md ; aucun backend/bucket créé ici. Le détenteur du vrai state doit migrer puis vérifier plan sans changement, accès/versioning/verrouillage. Aucun apply avec state vide. Étape 4.3 terminée, étape 4.2 À vérifier ; l’étape 4 complète reste En cours avant passage à 5.

## Mise à jour du 4 novembre 2026 (Jérémy)

L’action 4.2 est terminée : state migré vers un backend GCS privé, versionné et verrouillé, plan sans changement (code 0). L’étape 4 est close. Voir `rendu/Etape_4_2_V2_Verifications.md`.

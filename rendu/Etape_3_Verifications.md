# Étape 3 — vérifications du 2 novembre 2026

Session de Matis, avec assistance de l’IA. Sources : plan scolaire (étapes 3 et 7), SQL du TD 2 et format fichiers du TD 3.3.

## Réalisé

- Dossier Sideflix et dépôt Git local sur la branche `main` ; README et six dossiers prévus créés. Les TD originaux sont conservés.
- Base PostgreSQL locale `sideflix` créée et SQL exécuté : table `public.catalog` avec 6 contenus.
- Trois fichiers de sessions JSON créés, avec un objet par ligne et des identifiants fixes.

## Contrôles effectivement exécutés

| Contrôle | Résultat |
| --- | --- |
| Catalogue lu dans PostgreSQL | 6 contenus A à F |
| Clé primaire | Insertion d’un second A refusée |
| Contrainte de durée | Insertion d’une durée négative refusée |
| Trigger `updated_at` | Horodatage actualisé lors d’une modification du titre |
| Annulation des essais SQL | ROLLBACK ; 6 contenus conservés, aucun titre de test |
| Lecture des fichiers JSON | 32 objets lisibles, mêmes six champs |
| Répartition des lignes | 30 octobre : 3 ; 31 octobre : 15 ; 1er novembre : 14 |
| Liens avec le catalogue | Tous les content_id existent |
| Dates et appareils | UTC ; web, mobile ou tv |
| Doublon volontaire | S4 apparaît exactement deux fois, avec un contenu identique |
| Anomalie volontaire | S31 : -60 secondes ; seule session hors des bornes de durée |
| Sessions valides après retrait des anomalies et dédoublonnage | 30 |
| Référence du 30 octobre, calcul local à partir des fichiers | A : 2 sessions / 45 min ; B : 1 session / 10 min ; total : 3 sessions / 55 min |

## Fichiers utiles et reproduction

- `source/01_create_catalog.sql` : structure, contraintes, trigger et données fictives.
- `source/02_verify_catalog.sql` : contrôles PostgreSQL dans une transaction annulée ; à lancer avec `psql -X -h 127.0.0.1 -v ON_ERROR_STOP=1 -d sideflix -f source/02_verify_catalog.sql`.
- `source/sessions/sessions_2026-10-30.json`, `sessions_2026-10-31.json`, `sessions_2026-11-01.json` : données brutes à charger.
- `rendu/catalogue_postgresql.csv` : export réel du catalogue, dates UTC.
- `rendu/verification_postgresql.txt` : sortie réelle des contrôles SQL.

Les fichiers bruts conservent l’anomalie et le doublon. Le calcul local vérifie le jeu de référence ; la preuve du résultat produit par dbt dans Snowflake sera réalisée aux étapes 6 et 7.

## Reprise du travail

Étape 3 terminée. Prochaine action : étape 4, configurer Snowflake et le warehouse Terraform en adaptant le TD 4.2. Aucun objet Snowflake, job d’ingestion, modèle dbt ou DAG Sideflix n’a encore été créé.

Le dépôt Git est local, sans dépôt distant. Pour travailler sur un autre poste, récupérer les fichiers puis appliquer les commandes du README ; la base PostgreSQL ne se synchronise pas via Notion ou Git. La publication du dépôt pour le groupe reste à faire.

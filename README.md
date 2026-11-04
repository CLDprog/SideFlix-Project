# Sideflix — projet scolaire (travail interne du groupe)

Plateforme fictive de streaming indépendant inspirée de Netflix réel. Hypothèses : 10 000 abonnés à 7,99 €/mois, 100 contenus et 6 salariés. La revente à Netflix est une porte de sortie hypothétique.

**Cas d’usage conservé :** aider le responsable du catalogue à choisir les mises en avant hebdomadaires. Calcul quotidien à 06 h Paris, disponible avant 07 h. Grain : contenu et jour UTC de début de session. Indicateurs : sessions valides distinctes et somme des secondes visionnées / 60. Classement sur sept jours.

## Où nous en sommes — reprise du 4 novembre 2026

| Partie | État réel |
| --- | --- |
| Ancien prototype, étapes 3–5 | Catalogue fictif PostgreSQL, 32 lignes JSON, Snowflake et Terraform réalisés par le groupe ; ingestion/replay vérifiés. Scripts préservés. |
| Étape 6 | Projet dbt et preuves de son exécution Workspaces intégrés au dépôt : 6 contenus, 30 sessions valides, un rejet, un doublon ; Gold de référence 55 min. Tests de l’étape 7 encore à réaliser. |
| Reprise Framework, étape 2.1 | Cinq jeux publics collectés localement ; manifeste, mapping six films et catalogue réel CSV préparés. Conditions/attributions, périodes/grains et curation documentés dans `docs/sources_and_catalogue.md` ; étape 2 validée en conception. |
| Étape 2.2 | Architecture v2 vérifiée contre les sources, le cas d’usage et les méthodes des TD ; réalisation cloud v2 encore à exécuter. |
| Étape 3.2 v2 | Catalogue réel chargé et vérifié dans PostgreSQL local ; référence fictive sauvegardée, replay sans changement, contraintes et trigger testés. |
| Étape 4.3 v2 | Cinq tables Bronze/métadonnées préparées dans Snowflake ; sept contrôles réels OK, prototype conservé. |
| Étape 4.2 v2 | State Terraform migré vers un backend GCS privé, versionné et verrouillé ; plan sans changement (code 0). Étape 4 terminée. Preuves : `rendu/Etape_4_2_V2_Verifications.md`. |
| Étape 3.3 v2 | Sessions simulées préparées et contrôlées ; 32 brutes, 30 valides. Résultats attendus en CSV. |
| Étape 5 v2 | Terminée : cinq sources réelles et 32 sessions simulées chargées, catalogue synchronisé, rejeu sans nouvelle ligne et test de mise à jour en LAB réussis. Voir `rendu/Etape_5_V2_Verifications.md`. |
| Étape 6 v2 | 11 modèles exécutés en Core, contexte des cinq sources et chiffres métier vérifiés. Voir `rendu/Etape_6_V2_Verifications.md`. |
| Étape 7 v2 | Build 33/33 (21 tests), fraîcheur 2/2, exemples métier indépendants vérifiés. Voir `rendu/Etape_7_V2_Verifications.md`. |
| Étape 8 v2 | Terminée. Exécutée dans Docker/Airflow (TD 4.2) sur le PC de Jérémy : run du 1er novembre et rejeu réussis (build 33/33, une ligne publiée par date), journée sans données en échec bloquant avec retries, alerte reçue sur Slack. Base source en conteneur, snapshots partagés. Voir `rendu/Etape_8_V2_Verifications.md`. |
| Étape 9 v2 | Terminée : incident qualité bloquant, alerte reçue et reprise ; crash après écriture et retry sans doublon ; procédure fichier manquant ; deux runs normaux stables. Voir `rendu/Etape_9_V2_Verifications.md`. |
| Étape 10 | En cours : mesure Query Profile réelle et procédure arrêt/reprise documentées ; scripts administratifs prêts dans `governance/`. Rôles limités, crédits réels et moniteur nécessitent Jérémy en ACCOUNTADMIN. Voir `rendu/Etape_10_V2_Verifications.md`. |
| Suite | Clôturer10 après intervention administrative et run sous rôle limité, puis livrables et remise finale propre. |

La reprise porte sur les données et leurs adaptations ; le socle technique est réutilisé. Le Framework impose cinq jeux authentiques : IMDb, MovieLens, Netflix Top 10, Wikidata et Wikimedia. Les sessions Sideflix sont **simulées** et ne comptent pas parmi ces cinq jeux. Notes, consultations et classements externes ne sont pas des minutes regardées sur Sideflix.

## Dossiers et méthodes du cours

- `source/real/` : snapshots publics locaux, ignorés par Git ; URLs et empreintes dans `source/sources_manifest.csv`.
- `source/content_mapping.csv`, `catalog_real.csv` : correspondances IMDb/MovieLens/Wikidata/article, catalogue réel.
- `source/fixtures/reference/` : ancien jeu contrôlé conservé ; fichiers historiques aussi présents à leur emplacement initial.
- `source/v2/sessions/` et `expected_daily_usage.csv` : simulation finale isolée et résultats attendus.
- `ingestion/` : code de Jérémy conservé, watermark/MERGE et PUT/COPY des TD 2/3.3. Il traite désormais le catalogue réel et les cinq sources v2 ; les preuves du prototype sont conservées.
- `dbt/sideflix_dbt/` : modèles Silver/Gold déjà exécutés sur le prototype ; profil fourni réservé à Workspaces.
- `terraform/` : warehouse existant ; state partagé sur GCS (`backend.tf`), jamais recréer depuis un state vide. Voir `terraform/README.md`.
- `rendu/` : preuves de travail internes, pas un paquet final de remise.

Schéma détaillé : [architecture v2](docs/architecture_v2.md).

Architecture cible : catalogue IMDb → PostgreSQL → watermark/MERGE ; fichiers MovieLens/Netflix et sessions simulées → stage/COPY ; APIs Wikidata/Wikimedia → Python requests/VARIANT ; Snowflake Bronze → Silver/quarantaine → contrôles → Gold → Snowsight. Docker exécute, Airflow ordonnance seul ; Terraform gère l’infrastructure. Pas de déploiement supplémentaire lié au seul nom Netflix.

## Reprendre sur son poste

```sh
git pull --ff-only
python -m pip install -r source/requirements.txt
python source/collect_public_data.py
```

Le collecteur récupère les fichiers manquants et réutilise les snapshots présents ; les APIs ont timeout, échec HTTP visible et reprise limitée des erreurs 429. Les valeurs des sources publiques peuvent évoluer : consulter les empreintes/périodes et ne pas remplacer silencieusement un snapshot de démonstration. Voir `source/README.md` et `rendu/Collecte_V2_Verifications.md`.

Le profil dbt fourni fonctionne dans Snowsight Workspaces avec la session du groupe. Pour dbt Core/Docker, le profil à variables/RSA se trouve dans `dbt/profiles-core/` ; son exécution Core a été vérifiée. Aucune clé, mot de passe, webhook, `.env` ou state ne doit être versionné.

Les anciens scripts `source/01_create_catalog.sql` et `source/02_verify_catalog.sql` reproduisent le **fixture historique fictif**, pas le nouveau catalogue réel. Ne pas les présenter comme l’adaptation v2 ni remplacer les données du groupe avant intégration contrôlée.

## Collaboration et rendu

[Roadmap et avancement Notion — interne](https://app.notion.com/p/40cf4ba8c522812db500d27d4f5662c4). Les consignes actuelles viennent du Framework, du resource pack, des cours/TD et de Demo Content ; le PDF initial décrit l’ancien périmètre. Pas de rôles fixes : prendre une tâche disponible, indiquer son responsable temporaire et documenter résultats/commit dans Notion en fin de session.

Ce dépôt contient l’historique de travail du groupe. La remise à la professeure sera une copie distincte des seuls éléments exigés et correspondant à la version finale, avec accès vérifiés, sans lien vers les brouillons/archives internes. Conserver les tests et deux incidents/reprises exigés, ainsi que les limites et origines des données. Ce dépôt n’est pas encore le rendu final.

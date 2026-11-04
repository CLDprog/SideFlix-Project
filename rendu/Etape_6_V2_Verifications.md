# Étape 6 v2 — dbt exécuté et résultats vérifiés

4 novembre 2026, Matis. Précondition : étape 5 v2 clôturée (c74a961), cinq sources effectivement chargées, lots et rejeu contrôlés.

## Réalisation

Projet dbt existant réutilisé : cinq modèles historiques adaptés, cinq vues Silver externes ajoutées et une table Gold éditoriale. Méthodes TD 3.2/3.3 et pack 03 : source/ref, TRY_TO_*, LATERAL FLATTEN, ROW_NUMBER/QUALIFY, quarantaine et tables Gold reconstruites. Pas de Materialized View ni de fonction Enterprise.

Profil Core/Docker sans secret dans `dbt/profiles-core/profiles.yml` ; le profil Workspaces reste distinct. Versions réellement exécutées : dbt Core 1.11.16 et adaptateur Snowflake 1.11.6 (versions du Docker runner du pack), connector 4.8.0. Installer `dbt/requirements.txt`. La désactivation de la détection de plateforme doit être exportée avant dbt, comme ci-dessous.

Les lots publics et simulés sont explicitement fixés dans `dbt_project.yml` à ceux du reçu de l'étape 5. Un rafraîchissement nécessite de mettre ces variables à jour après vérification du reçu. Les anciennes sessions ne sont pas sélectionnées. Le catalogue réel garde ses identifiants/provenances ; chaque Silver externe conserve source, lot, fichier et chargement. Les vues ne modifient aucune Bronze.

Dédoublonnage : version la plus récente selon date de chargement (ou date source des notes), puis lot/fichier et contenu stable de la ligne. Sessions : _loaded_at DESC, lot, fichier, date source et champs métier ; les égalités exactes sont équivalentes. Le doublon S4 donne une seule session. Quarantaine : S31, -60 secondes, `invalid_watched_seconds`, avec RAW et métadonnées. Les devices restent visibles pour le test accepted_values de l'incident futur.

Notes MovieLens agrégées par IMDb, pageviews par article, Netflix par contenu confirmé, tous AVANT jointure aux métriques. Les deux observations Get Out non confirmées restent en Silver sans appariement ; seule la correspondance Sicario E est confirmée. Les valeurs absentes restent NULL, jamais un zéro fabriqué. Gold lit uniquement Silver ; jour de session UTC, planification Paris distincte.

## Résultats réellement obtenus

- dbt run puis reconstruction réussis : 11 modèles + hook, PASS=12, WARN=0, ERROR=0. Les avertissements de configuration obsolète seront nettoyés lors de l'ajout des tests.
- Silver : IMDb 6, catalogue 6, staging 32, quarantaine 1, sessions retenues 30, notes agrégées 6 œuvres, Netflix 3 observations, Wikidata 6 œuvres, Wikimedia 42 article/jours.
- Gold quotidien : 14 contenu/jours, tous comparés au CSV attendu calculé indépendamment. 30 octobre : A=2 sessions/45 minutes ; B=1/10 ; total 55 minutes.
- Gold éditorial : 6 œuvres, total 30 sessions et somme des minutes identique au quotidien. Les cinq sources contribuent ; 6 notes/métadonnées/pageviews présents et une correspondance Netflix confirmée. Gagnant : Whiplash, 7 sessions, 112,666667 minutes ; classement fondé seulement sur les métriques Sideflix simulées.
- Les périodes externes, le statut Netflix, l'indicateur simulation et `published_at_utc` sont visibles dans la table ; pas de score composite. Ce timestamp indique la construction du tableau ; à l'étape 7 le build/tests devra valider sa publication.

## Commandes et preuves

```sh
export SNOWFLAKE_DISABLE_PLATFORM_DETECTION=true AWS_EC2_METADATA_DISABLED=true DBT_SEND_ANONYMOUS_USAGE_STATS=false
.venv/bin/dbt run --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
.venv/bin/dbt docs generate --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
.venv/bin/python ingestion/verify_dbt_v2.py
```

Variables Snowflake/RSA chargées depuis le fichier privé local, jamais depuis Git. Preuves : `dbt_6_v2_run.txt`, `dbt_6_v2_replay.txt`, `dbt_6_v2_docs.txt`, `dbt_6_v2_business_checks.txt`, `gold_editorial_v2.csv`. Catalogue/lineage dbt générés dans le dossier `target/` ignoré ; régénérables avec la commande ci-dessus.

Suite : étape 7, tests dbt/build et fraîcheur ; étape 8 Docker/Airflow non validée. Le test d'accès Docker de cette session renvoie « permission denied while trying to connect to the docker API » ; ne pas annoncer une exécution conteneurisée réussie.

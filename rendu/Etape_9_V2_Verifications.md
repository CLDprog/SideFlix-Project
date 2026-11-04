# Étape 9 v2 — en cours sur le Mac de Matis

Étape 8 de Jérémy vérifiée dans ses preuves, commit 3106d9f. Aucune des sous-étapes 9.1–9.4 n'est encore déclarée terminée.

## Préparation réelle

- Docker démarré par Matis depuis son terminal (moteur 29.3.1). L'assistant n'a pas accès au socket ; il n'en contourne pas les permissions.
- Base Airflow locale consultée en lecture seule : `sideflix_daily` existe, est en pause, zéro erreur d'import. « No data found » de la CLI ne signifie donc pas que le fichier DAG manque.
- Configuration privée Mac préparée ; présence du webhook vérifiée sans afficher sa valeur.
- État Snowflake avant incident enregistré dans `incident_9_v2_before.json` : Gold quotidienne, Gold éditoriale et ligne de publication du 1er novembre. Aucune donnée modifiée par ce contrôle.

## Options de démonstration (méthodes TD 3.2/4.2)

Le DAG normal est inchangé sans paramètre `incident`. Les options ne sont actives que dans le run manuel concerné :

- 9.1 : configuration `{"date":"2026-11-01","incident":"bad_device"}`. Le chargeur crée en mémoire une copie des 32 sessions, remplace S1 par TEST_BAD_DEVICE/device=invalid dans cette copie, puis charge un lot distinct via le même PUT/COPY. Le nombre de lignes et les durées restent identiques pour atteindre le test accepted_values, sans échec prématuré de complétude. Le run_id distingue chaque lot de test. Le reçu dirige dbt vers cette copie ; aucun snapshot de référence n'est écrit ni modifié. Les reprises du même run réutilisent le même lot. Attendu, à vérifier réellement : échec du test, Gold/publication conservées, alerte après dernier retry.
- Correction 9.1 : après capture de l'échec, retirer le lot de démonstration identifié par son batch_id exact, puis relancer sans option d'incident pour sélectionner les sessions de référence. Aucun autre lot ne doit être supprimé. Vérifier le retour au vert et les chiffres de référence.
- 9.2 : configuration `{"date":"2026-11-01","incident":"crash_after_write"}` transmet `--crash-on-try 1` au script de publication existant, comme au TD4.2. Attendu : premier échec après MERGE, retry réussi, une ligne/date. Ne l'exécuter qu'après clôture 9.1.
- 9.3 : courte procédure fichier manquant à documenter ensuite ; pas de troisième simulation requise.
- 9.4 : deux runs normaux, résultats stables et comptes rendus des incidents.

Les injections restent désactivées dans tous les runs sans option `incident`. Les fichiers générés de landing sont ignorés par Git. Après les runs, ne conserver aucun changement d'horodatage du manifeste/catalogue si les empreintes et valeurs sont inchangées.

## Statut

Options préparées et syntaxe Python vérifiée. Incidents non exécutés à ce stade ; réception des alertes et reprise restent à prouver. Prochaine action : reconstruire l'image ingestion dans le terminal de Matis, laisser Airflow charger le DAG modifié, puis déclencher uniquement 9.1. Conserver logs/états/notifications/avant-après dans rendu et actualiser Notion après résultats réels.

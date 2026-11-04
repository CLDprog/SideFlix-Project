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

## 9.1 — panne effectivement exécutée, reprise normale encore attendue

Run `matis_9_1_bad_device`, sur Docker/Airflow du Mac, 4 novembre 2026. Ingestion et check_sources réussis. Les trois tentatives de dbt_build échouent exclusivement sur `accepted_values_silver_sessions_device__web__mobile__tv` (1 valeur fautive) : PASS=28, ERROR=1, SKIP=4. Les deux tables Gold et leurs tests sont SKIP ; `publish_daily_usage` est upstream_failed, tentative0. Après le dernier échec, callback `ALERT_DELIVERED_HTTP 200` ; confirmation visuelle dans le canal encore à obtenir.

Comparaison Snowflake intégrale avec `incident_9_v2_before.json` : Gold quotidienne, Gold éditoriale (timestamps compris) et publication du 1er novembre strictement inchangées. La session TEST_BAD_DEVICE/invalid a été constatée dans Silver, exclusivement issue du lot de démonstration `sessions_simulated_96d78fad181a1ed6db07727b`.

Correction ciblée exécutée après fin du run et des retries : suppression des 32 lignes de cette seule copie de test en Bronze. Le lot original de32lignes est préservé. Les fichiers de référence n'ont pas été modifiés ; les19empreintes du manifeste restent identiques. Les seuls horodatages réécrits par le collecteur ont été remis à la version du dépôt après comparaison de toutes les autres valeurs. Le journal d'ingestion de ce lot reste comme preuve historique ; la copie de données de test a été retirée.

**Prochaine action obligatoire :** déclencher le run normal `matis_9_1_fixed` avec `{"date":"2026-11-01"}` pour reconstruire Silver depuis le lot original et valider le retour au vert. Ne pas utiliser le même run_id que la panne. L'étape9.1 reste en cours tant que cette reprise et ses chiffres ne sont pas vérifiés. Ne pas déclencher9.2 avant.

Cause : catégorie device hors des valeurs autorisées sur une copie isolée. Impact évité : publication de données non validées. Détection : accepted_values et échec Airflow après retries, alerte HTTP200. Reprise : retrait de la seule copie fautive puis run normal. Prévention : test bloquant avant Gold/publication ; options d'incident désactivées par défaut.

Preuves brutes : `incident_9_1_logs/` (ingestion, contrôle, trois builds), `incident_9_1_failed_and_cleanup.json` (états, comparaison avant/après, nettoyage), `incident_9_v2_before.json` (référence). Aucun incident9.2 exécuté.

## 9.1 terminée — reprise vérifiée, 4 novembre 2026

Matis confirme la réception dans Slack de l'alerte de dbt_build, tentative3, à18h13 Paris (preuve `incident_9_1_slack_confirmation.txt`). Le run correctif `matis_9_1_fixed`, sans option d'incident, a réussi ses quatre tâches ; dbt build PASS33/WARN0/ERROR0/SKIP0. Contrôle Snowflake réel : publication du1er novembre unique,13sessions/177,4minutes, run_id correctif ;30sessions Silver uniques ; aucune TEST_BAD_DEVICE ni catégorie invalid ; copie de test absente ;14résultats Gold quotidiens strictement identiques à l'avant-incident ;6œuvres éditoriales et30sessions au total. Les19empreintes restent conformes au manifeste. Les modifications d'horodatages seules ont été remises à la version Git.

Preuves de reprise : `incident_9_1_recovery.json` et `incident_9_1_recovery_logs/`. Les étapes panne/détection/blocage/notification/correction/reprise sont maintenant toutes vérifiées pour9.1. Étape9 globale encore en cours : prochaine action9.2, crash après écriture avec retry, non encore exécuté.

# Étape 10 — terminée et vérifiée (intervention administrative réalisée le 4 novembre)

**Mise à jour du 4 novembre 2026, 19 h 20 (Jérémy) : intervention administrative faite et vérifiée.** Rôles limités créés, refus réels prouvés, run Airflow normal exécuté sous SIDEFLIX_RUNNER par un utilisateur de service dédié, moniteur de ressources rattaché, crédits et stockage réels relevés (dernière section). Notifications e-mail du moniteur activées par Jérémy dans son profil Snowsight le 4 novembre à 19 h 50 : **étape 10 terminée.**

4 novembre2026. Étapes1–9 terminées et vérifiées avant cette étape. Aucun Terraform exécuté ni objet REDGRAVE modifié.

## 10.1 — sécurité et gouvernance

Matis ne dispose que de SYSADMIN pour Sideflix ; création des rôles et moniteur réservée à Jérémy. Le DAG précédent s'exécute sous SYSADMIN, jamais ACCOUNTADMIN, mais SYSADMIN reste trop large. Script administratif concret : `governance/10_admin_setup.sql`, puis contrôles `10_verify_access.sql`. Les rôles limités, refus et exécution du DAG sous runner restent à vérifier ; aucune réussite annoncée.

Préparation du code : variable runtime SNOWFLAKE_ROLE dans helper RSA, profil Core et DAG, défaut historique SYSADMIN préservé jusqu'aux grants ; création inutile de schéma retirée du hook dbt (LAB existe déjà). Vérification syntaxique effectuée ; ces adaptations ne constituent pas encore une exécution au moindre privilège.

Protection vérifiée : aucun .env, fichier de clé privée ou state suivi par Git ; exclusions .gitignore/.dockerignore ; clé montée read-only, webhook passé au runtime, non intégré à l'image. Backend du state : GCS privé/versionné/verrouillé selon les preuves réelles4.2, accessible à Jérémy. Pas de revalidation cloud du bucket depuis Matis. Données Sideflix simulées identifiées ; sources publiques, périodes et attributions dans docs/sources_and_catalogue et manifeste. Mise à jour du 4 novembre, 23 h : la remise est ce dépôt privé, sans copie distincte ; les exports IMDb/Netflix y restent versionnés (commit 0577f62) pour le rejeu exact, et le dépôt n’est pas rendu public tant qu’ils y figurent, historique compris.

## 10.2 — configuration et performance réellement relevées

Preuve brute : `Etape_10_Mesures.json`. SHOW WAREHOUSES : SIDEFLIX_WH, X-Small, STANDARD_GEN_2, auto-suspend60s, auto-resume=true. Aucun resource monitor rattaché à ce stade (SHOW RESOURCE MONITORS vide). Le flag query_acceleration est déjà true dans la configuration observée ; il n'a pas été activé pendant cette étape et aucune dépense associée n'est inventée.

Requête Sideflix : filtre direct usage_date=2026-11-01, SUM des sessions/minutes par content_id, sur Gold quotidien. Query_id `01c830d1-0002-558c-0002-e4f2001372ea` : temps total248ms, exécution24ms,3072octets scannés,6lignes. Profil TableScan :3partitions sur5,100% des octets depuis le cache de données. USE_CACHED_RESULT=false pendant la mesure, puis valeur initiale true rétablie. Cache de résultat désactivé ne signifie donc pas cache de données froid. Aucun gain arbitraire, clustering ou autre optimisation ajouté.

L'essai de lecture des colonnes PARTITIONS_SCANNED directement dans QUERY_HISTORY_BY_SESSION a renvoyé invalid identifier ; ces champs n'y sont pas exposés dans cet environnement. Mesure corrigée via GET_QUERY_OPERATOR_STATS, méthode fournie dans Demo Content. Les valeurs ci-dessus sont réellement obtenues, pas celles des démos.

## Consommation et projection30jours

ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY et TABLE_STORAGE_METRICS : accès refusé à SYSADMIN (« schema does not exist or not authorized »). Le table function WAREHOUSE_METERING_HISTORY a renvoyé0ligne : cela ne vaut pas0crédit. Les crédits réellement consommés et le stockage facturable restent donc à relever par Jérémy avec le script administratif.

Projection explicite de compute, non facture : hypothèse1run/jour,2minutes de warehouse actif par run (environ1min d'exécution observée en8/9 +60s d'auto-suspend),1cluster X-Small Gen2 AWS,30jours. Tarif de consommation officiel Gen2 AWS :1,35crédit/heure, soit30 × (120/3600) ×1,35 = **1,35crédit/30jours**. Dix runs/jour donneraient13,5crédits, montrant l'effet des répétitions de développement. Hypothèse de120s non mesurée comme temps facturé exact ; réveils supplémentaires, maintien ouvert et services cloud peuvent augmenter la consommation.

Source officielle consultée le4novembre2026 : Snowflake Service Consumption Table, table1(b), effective4novembre2026 : https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf . Pas de conversion monétaire sans prix effectif du compte. Le crédit d'essai n'est pas un coût nul.

Stockage : bruts Git privés8,51Mo hors caches ; stockage Snowflake actif/time-travel/failsafe encore à relever, pas déduit du volume Git. Backend réel GCS pour le state (et non S3, ancienne option de roadmap abandonnée) : coût réel non disponible sur le poste de Matis ; vérifier sur le compte Google de Jérémy. Docker/PostgreSQL/Airflow sont locaux. Pas d'autre ressource cloud déclarée ici.

Contrôle choisi : moniteur10crédits/mois, notifications50/80%, suspension100%, rattaché uniquement à SIDEFLIX_WH. Script prêt, mais moniteur/notifications non encore configurés ni validés. Ne pas brûler des crédits pour une démonstration d'alerte budgétaire ; conserver SHOW du monitor et du rattachement, configuration de notification/visibilité prévue. Revoir un futur plan Terraform pour préserver ce rattachement manuel.

## 10.3 — arrêt/reprise et nettoyage futur

Procédure courte dans `governance/README.md` : pause DAG, down sans suppression des volumes, suspension warehouse, puis up/contrôle/réactivation/run normal pour l'oral. Les mêmes commandes Compose/CLI ont été utilisées réellement en8/9 ; arrêt complet non déclenché ici pendant la préparation. Nettoyage strictement ciblé et différé après correction, depuis le bon state pour IaC ; aucune destruction avant l'oral.

## Reste avant clôture (état avant l'intervention, conservé comme historique)

Jérémy exécute le script administratif et fournit sorties de grants/monitor, crédits et stockage. Ensuite Matis peut vérifier analyste seul (GoldSELECT oui, BronzeSELECT et GoldINSERT non), reconstruire les images et exécuter un run normal sous SIDEFLIX_RUNNER. Étape10 non terminée avant ces preuves ;10.2 reste bloquée sur coûts réels/moniteur,10.1 sur rôles/tests. _Mise à jour : intervention réalisée le 4 novembre par Jérémy (section suivante, commits ea4d78d et b77ff6d) ; étape 10 terminée._

## Intervention administrative et validations réelles : 4 novembre 2026, 19 h 10 à 19 h 20 (Jérémy)

Exécutée depuis le PC de Jérémy, en ACCOUNTADMIN par connexion par clé (aucun mot de passe), avec `governance/10_admin_setup.sql` de Matis sans modification, puis `governance/10b_pipeline_user.sql`. Aucun objet REDGRAVE ni ressource Terraform modifié. Sortie complète : `Etape_10_admin_outputs.txt`.

### Ajout : utilisateur de service dédié au pipeline

Le script de Matis n'accordait SIDEFLIX_RUNNER qu'à MATIS_DOUAY. Sur le poste de démonstration de Jérémy, les jobs se connectaient avec un utilisateur disposant d'ACCOUNTADMIN : ils n'auraient pas réellement tourné au moindre privilège. `10b_pipeline_user.sql` crée donc `SIDEFLIX_PIPELINE` (TYPE=SERVICE, rôle par défaut SIDEFLIX_RUNNER, aucun rôle secondaire, pas de mot de passe), avec une nouvelle paire de clés générée par `gen_key.py` du TD 2. La clé privée reste hors Git (`C:/Users/jerem/sideflix_keys`), montée en lecture seule ; empreinte enregistrée `SHA256:ypAUUv/nAeoxCH8PpvzT6RXVnr5hlHhxwjStY1dPhNg=`.

### 10.1 : autorisations et refus réels (`Etape_10_access_tests.txt`, 11 contrôles, 11 conformes)

| Contexte | Action | Attendu | Obtenu |
| --- | --- | --- | --- |
| SIDEFLIX_ANALYST seul, `USE SECONDARY ROLES NONE` | SELECT Gold | autorisé | autorisé (3 lignes) |
| idem | SELECT Bronze, SELECT Silver | refusé | refusé (schéma non autorisé) |
| idem | INSERT Gold de 0 ligne | refusé | refusé (INSERT non accordé) |
| SIDEFLIX_PIPELINE, rôle SIDEFLIX_RUNNER, secondaires vides | SELECT Bronze et Gold | autorisé | autorisé |
| idem | USE ROLE ACCOUNTADMIN / SYSADMIN | refusé | refusé (rôle non attribué) |
| idem | CREATE SCHEMA, lecture ACCOUNT_USAGE, lecture base REDGRAVE | refusé | refusé |

Run Airflow normal `runner_normal_20261101` (`Etape_10_runner_run.txt`) après reconstruction des deux images et `SNOWFLAKE_USER=SIDEFLIX_PIPELINE`, `SNOWFLAKE_ROLE=SIDEFLIX_RUNNER` dans le `.env` privé : quatre tâches en succès en 1 min 29 s ; 94 requêtes Snowflake, toutes par SIDEFLIX_PIPELINE avec le rôle SIDEFLIX_RUNNER, aucune en erreur ; 6 lots identiques, 0 nouvelle ligne ; freshness puis build PASS=33 ; publication 13 sessions, 177,4 minutes, une seule ligne pour le 2026-11-01. Le DAG ne tourne donc plus avec un rôle administrateur.

### 10.2 : coûts réels, projection et moniteur

Crédits réellement consommés par SIDEFLIX_WH (ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY, relevé à 18 h 10 UTC, latence possible de quelques heures) : 0,164 crédit le 3 novembre, 1,277 le 4 novembre jusqu'à 19 h 00 UTC, soit **1,44 crédit** au total (compute + services cloud). Ce sont surtout des runs de développement et d'incidents répétés, pas le rythme cible.

Stockage SIDEFLIX (TABLE_STORAGE_METRICS) : 0,48 Mo actifs, 25,1 Mo en time travel (réécritures Bronze par COPY/MERGE), 3,5 Ko en fail-safe. Volume négligeable, facturé au To par mois : pas de montant inventé.

Projection 30 jours, à partir du run réel sous SIDEFLIX_RUNNER : requêtes actives de 18:13:54 à 18:15:05 (71 s) plus 60 s d'auto-suspend, soit environ 131 s de warehouse par run quotidien. 30 × 131/3600 h × 1,35 crédit/h (X-Small Gen2, table de consommation citée plus haut) ≈ **1,5 crédit par mois**. Hypothèses : un run par jour, aucune autre requête ; chaque réveil supplémentaire coûte au minimum 60 s.

Moniteur `SIDEFLIX_MONTHLY` créé et rattaché : quota 10 crédits par mois, notifications à 50 et 80 %, suspension à 100 %, niveau WAREHOUSE ; `SHOW WAREHOUSES` : SIDEFLIX_WH X-Small, auto-suspend 60 s, auto-resume, resource_monitor SIDEFLIX_MONTHLY. Le quota laisse une marge large au-dessus de la projection (1,5) et de la consommation de développement observée. Aucune consommation artificielle pour déclencher un seuil. Les notifications e-mail d'un moniteur sont envoyées aux administrateurs du compte qui les ont activées dans leur profil Snowsight : activées par Jérémy le 4 novembre à 19 h 50.

### Suite

Le plan Terraform reste à relire depuis le backend GCS avant tout futur apply, pour ne pas retirer le rattachement manuel du moniteur. MATIS_DOUAY dispose aussi des deux rôles limités (rôles secondaires par défaut neutralisés) pour ses propres runs.


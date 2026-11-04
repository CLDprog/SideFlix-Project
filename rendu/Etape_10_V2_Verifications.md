# Étape 10 — en cours, intervention administrative nécessaire

4 novembre2026. Étapes1–9 terminées et vérifiées avant cette étape. Aucun Terraform exécuté ni objet REDGRAVE modifié.

## 10.1 — sécurité et gouvernance

Matis ne dispose que de SYSADMIN pour Sideflix ; création des rôles et moniteur réservée à Jérémy. Le DAG précédent s'exécute sous SYSADMIN, jamais ACCOUNTADMIN, mais SYSADMIN reste trop large. Script administratif concret : `governance/10_admin_setup.sql`, puis contrôles `10_verify_access.sql`. Les rôles limités, refus et exécution du DAG sous runner restent à vérifier ; aucune réussite annoncée.

Préparation du code : variable runtime SNOWFLAKE_ROLE dans helper RSA, profil Core et DAG, défaut historique SYSADMIN préservé jusqu'aux grants ; création inutile de schéma retirée du hook dbt (LAB existe déjà). Vérification syntaxique effectuée ; ces adaptations ne constituent pas encore une exécution au moindre privilège.

Protection vérifiée : aucun .env, fichier de clé privée ou state suivi par Git ; exclusions .gitignore/.dockerignore ; clé montée read-only, webhook passé au runtime, non intégré à l'image. Backend du state : GCS privé/versionné/verrouillé selon les preuves réelles4.2, accessible à Jérémy. Pas de revalidation cloud du bucket depuis Matis. Données Sideflix simulées identifiées ; sources publiques, périodes et attributions dans docs/sources_and_catalogue et manifeste. La remise finale devra exclure exports IMDb/Netflix et historique interne.

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

## Reste avant clôture

Jérémy exécute le script administratif et fournit sorties de grants/monitor, crédits et stockage. Ensuite Matis peut vérifier analyste seul (GoldSELECT oui, BronzeSELECT et GoldINSERT non), reconstruire les images et exécuter un run normal sous SIDEFLIX_RUNNER. Étape10 non terminée avant ces preuves ;10.2 reste bloquée sur coûts réels/moniteur,10.1 sur rôles/tests.

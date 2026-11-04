# Étape 7 v2 — tests et vérifications métier

4 novembre 2026, Matis. Étapes 5 et 6 v2 vérifiées et clôturées avant cette étape.

## Tests réellement exécutés

`dbt build` : **PASS=33, WARN=0, ERROR=0, SKIP=0**, soit 11 modèles, 21 tests et un hook. Clés uniques/non nulles, relation contenu/session, types/device autorisés, durées, grains externes, périodes pageviews, couverture des cinq jeux, réconciliation 32=30+1+1 et égalité Silver/Gold avec absence d'inflation après enrichissement. Les tests sont ceux des TD et des tests SQL singuliers du pack ; aucun package de tests supplémentaire.

`dbt source freshness`, exécuté séparément : **2/2 PASS**, catalogue et lot de sessions simulées v2. Seuils : avertissement après 24 h, erreur après 26 h pour un flux quotidien. Ce sont des seuils de détection d'un chargement périmé ; ils ne prouvent pas à eux seuls l'échéance 07 h. Le planning/durée d'exécution Airflow devra apporter cette preuve à l'étape 8. Le catalogue peut légitimement ne pas changer lors d'un rejeu ; pour une simulation à date fixe, les lots et le manifeste restent les contrôles de référence.

Les cinq snapshots publics ne sont pas déclarés « frais » d'après leur ancienne date métier : la présence, le lot prévu, les empreintes et les volumes sont contrôlés. Notes MovieLens historiques 1996–2018, Netflix Sicario observé le 9 mars 2025, Wikimedia 26 octobre–1er novembre 2026. Une source requise manquante/vidée ou un mauvais nombre d'observations fait échouer `assert_public_completeness` ; ce test dépend aussi des sessions pour bloquer les deux tables Gold.

## Comparaisons indépendantes

Script `ingestion/verify_business_samples.py`, utilisant les fichiers sources, les réponses API réellement reçues et les tables de référence LAB :

| Exemple | Attendu recalculé | Observé cloud |
| --- | --- | --- |
| Fixture isolé LAB, 30/10 | 32 brutes = 30 valides + 1 rejet + 1 doublon ; A 45 min + B 10 min | A 2/45, B 1/10, soit 3 sessions / 55 min |
| Lot final A, 31/10 | 3 session_id distincts ; 2610 secondes /60 | 3 sessions /43,5 min |
| MovieLens Whiplash | 38 notes, somme 153,5 ; moyenne 4,0394736842 | 38 /4,0394736842 |
| Wikimedia Whiplash | Somme des sept jours reçus : 15 551 | 15 551 |
| Netflix Sicario | 09/03/2025, rang 5, une observation appariée | 09/03/2025, rang 5, une observation |

Tous les 14 résultats contenu/jour avaient aussi été comparés au CSV indépendant à l'étape 6. Les six œuvres du tableau éditorial gardent les mêmes totaux de consommation ; les périodes et l'origine simulée sont visibles.

## Preuves et reproduction

Avec les variables privées locales et l'environnement dbt décrit à l'étape 6 :

```sh
.venv/bin/dbt build --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
.venv/bin/dbt source freshness --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
.venv/bin/python ingestion/verify_business_samples.py
```

Preuves : `dbt_7_v2_build.txt`, `dbt_7_v2_run_results.json`, `dbt_7_v2_freshness.txt`, `dbt_7_v2_freshness_results.json`, `dbt_7_v2_business_samples.txt`. Lineage source/ref et documentation générables par `dbt docs generate`. Avertissements YAML/config du premier run nettoyés.

Étape 7 terminée pour les contrôles de référence. L'injection de device invalide, le blocage réel de publication et la reprise sont encore à exécuter à l'étape 9 ; aucun incident ni notification n'est déclaré réussi ici. Étape suivante : 8 Docker/Airflow, dont l'accès au daemon est actuellement refusé dans cette session. _Mise à jour du 4 novembre : étape 8 exécutée sur le PC de Jérémy (`Etape_8_V2_Verifications.md`), incidents 9.1 et 9.2 exécutés et repris (`Etape_9_V2_Verifications.md`)._

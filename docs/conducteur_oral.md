# Conducteur proposé — à confirmer à trois sur les14slides

Oral :6novembre2026 à13h, groupe6. Le créneau exact de parole n'a pas été relevé ; ne pas inventer une durée réglementaire. Les numéros de diapositives seront reportés après accès à l'export14slides. Ce document ne vaut pas répétition effectuée.

| Ordre/thème | Intervenant proposé | Ce qu'il montre et explique |
| --- | --- | --- |
| Besoin, scénario Sideflix/Netflix, décision | Matis | Utilisateur catalogue, hypothèses, grain/formules/exclusions ; cinéma indépendant et revente hypothétique |
| Sources et traitement | Matis | Cinq jeux réels distincts des sessions simulées ; watermark/MERGE, COPY, API/VARIANT ; Silver, tests et lineage |
| Infrastructure et exécution | Jérémy | Architecture exécutée, Snowflake/AWS, state GCS, Docker/PostgreSQL/Airflow, rôles limités et coûts ; déclenche réellement un run normal |
| Résultat et valeur métier | Rayan | Feuille Snowsight `sideflix_restitution_gold.sql`, rôle analyste seul (captures de secours : `rendu/Restitution_Snowsight.md`) : tableau/graphique Gold, Whiplash premier ; séparer minutes simulées, notes historiques, pageviews et Top10 externe |
| Fiabilité et gouvernance | Matis puis Jérémy | Preuves des deux incidents/reprises, publication unique ; autorisations/refus, moniteur, arrêt/reprise et limites |
| Conclusion et questions | Les trois | Une décision éditoriale, limites du prototype, contribution réelle de chacun |

Run normal : conf `{"date":"2026-11-01"}`, run_id neuf, sans clé incident. Résultats attendus :4tâches success, build33/33,13sessions/177,4min et une ligne de publication. Pendant l'exécution, montrer l'architecture ou les sources plutôt que rester sur un écran d'attente. Montrer ensuite la preuve, puis son interprétation métier.

Le poste de présentation et Docker restent allumés ; un seul Airflow actif. Refaire un run normal pour la répétition si nécessaire ; les deux incidents ont déjà leurs preuves réelles et leurs paramètres documentés. Ne pas déclencher bad_device dans la vidéo finale. Pour l'oral, préparer avec le groupe la démonstration des reprises à partir de `rendu/Etape_9_V2_Verifications.md`, sans toucher les données de référence ni utiliser ACCOUNTADMIN dans le DAG. Vidéo et logs sont des secours, pas le remplacement annoncé du run live.

À confirmer avant clôture11.6 : export14slides relu, répartition acceptée par les trois, présentation de la restitution Snowsight (exécutée et capturée par Matis le 4/11) par Rayan ou un autre membre, durée répétée et accès/réseau du poste de présentation.

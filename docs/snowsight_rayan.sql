-- Sideflix · restitution Snowsight depuis Gold, en lecture seule (rôle SIDEFLIX_ANALYST, sans rôle secondaire).
-- Feuille préparée pour Rayan, exécutée et capturée par Matis le 4/11/2026 : rendu/Restitution_Snowsight.md.
-- Légende : visionnages Sideflix SIMULÉS · fenêtre d'analyse du 26 octobre au 1er novembre 2026
-- sessions disponibles du 30 octobre au 1er novembre 2026 (jour UTC de début de session).
-- Notes MovieLens, vues Wikipédia et rangs Netflix : contexte externe daté, jamais des minutes Sideflix.
USE ROLE SIDEFLIX_ANALYST;
USE SECONDARY ROLES NONE;
USE WAREHOUSE SIDEFLIX_WH;
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();

-- 1. Tableau : classement éditorial de la semaine et contexte des cinq sources.
SELECT editorial_rank AS rang, title AS titre,
       valid_sessions AS sessions_valides, ROUND(minutes_watched, 1) AS minutes_regardees,
       DATEADD(day, -6, analysis_date) || ' → ' || analysis_date AS fenetre_analyse,
       sideflix_sessions_simulated AS sessions_simulees,
       ROUND(avg_rating, 2) AS note_movielens, rating_count AS nb_notes,
       ratings_start || ' → ' || ratings_end AS periode_notes,
       pageviews AS vues_wikipedia, views_start || ' → ' || views_end AS periode_vues,
       best_observed_rank AS rang_netflix, first_observed_week AS semaine_netflix, netflix_status AS statut_netflix,
       external_sources AS sources_externes, published_at_utc AS publie_utc
FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY
ORDER BY editorial_rank;

-- 2. Graphique : onglet Chart, barres, X = TITLE, Y = MINUTES_WATCHED (minutes simulées sur la fenêtre).
SELECT title, ROUND(minutes_watched, 1) AS minutes_watched
FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY
ORDER BY editorial_rank;

-- 3. Contrôle journalier indépendant (autre table Gold) : 13 sessions et 177,4 min le 1er novembre,
--    total de la fenêtre 30 sessions et 454,2 min, égal à la somme du tableau 1.
SELECT COALESCE(TO_VARCHAR(usage_date), 'TOTAL fenêtre') AS jour_utc,
       SUM(valid_sessions) AS sessions_valides, ROUND(SUM(minutes_watched), 1) AS minutes_regardees
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY
WHERE usage_date BETWEEN '2026-10-26' AND '2026-11-01'
GROUP BY ROLLUP (usage_date)
ORDER BY usage_date NULLS LAST;
-- Une feuille Snowsight est privée : les captures et sorties sont exportées dans rendu/ pour le jury.

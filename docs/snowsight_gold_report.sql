-- Sideflix: read-only Gold reporting in Snowsight (SIDEFLIX_ANALYST, no secondary roles).
-- Prepared for Rayan; executed and captured by Matis on 4 November 2026: evidence/08_gold_report/snowsight_report.md.
-- Caption: SIMULATED Sideflix viewing; analysis window 26 October to 1 November 2026.
-- Sessions are available from 30 October to 1 November (UTC session-start date).
-- MovieLens ratings, Wikipedia page views and Netflix ranks are dated external context, never Sideflix minutes.
USE ROLE SIDEFLIX_ANALYST;
USE SECONDARY ROLES NONE;
USE WAREHOUSE SIDEFLIX_WH;
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();

-- 1. Table: weekly editorial ranking and context from all five sources.
SELECT editorial_rank, title,
       valid_sessions, ROUND(minutes_watched, 1) AS minutes_watched,
       DATEADD(day, -6, analysis_date) || ' → ' || analysis_date AS analysis_window,
       sideflix_sessions_simulated,
       ROUND(avg_rating, 2) AS movielens_rating, rating_count,
       ratings_start || ' → ' || ratings_end AS rating_period,
       pageviews AS wikipedia_pageviews, views_start || ' → ' || views_end AS pageview_period,
       best_observed_rank AS netflix_rank, first_observed_week AS netflix_week, netflix_status,
       external_sources, published_at_utc
FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY
ORDER BY editorial_rank;

-- 2. Chart: bar chart, X = TITLE, Y = MINUTES_WATCHED (simulated minutes in the analysis window).
SELECT title, ROUND(minutes_watched, 1) AS minutes_watched
FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY
ORDER BY editorial_rank;

-- 3. Independent daily check from the other Gold table: 13 sessions / 177.4 minutes on 1 November.
--    Window total: 30 sessions / 454.2 minutes, matching the first table's totals.
SELECT COALESCE(TO_VARCHAR(usage_date), 'TOTAL window') AS utc_day,
       SUM(valid_sessions) AS valid_sessions, ROUND(SUM(minutes_watched), 1) AS minutes_watched
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY
WHERE usage_date BETWEEN '2026-10-26' AND '2026-11-01'
GROUP BY ROLLUP (usage_date)
ORDER BY usage_date NULLS LAST;
-- A Snowsight worksheet is private: exported screenshots and actual query outputs are in evidence/ for the jury.
-- Display aliases are now English; the historical execution JSON and screenshots preserve their original labels.

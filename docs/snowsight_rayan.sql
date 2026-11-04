-- Rayan: personal Snowsight worksheet, read-only Gold. No lab/source access needed.
USE ROLE SIDEFLIX_ANALYST;
USE SECONDARY ROLES NONE;
USE WAREHOUSE SIDEFLIX_WH;
SELECT CURRENT_USER(),CURRENT_ROLE(),CURRENT_SECONDARY_ROLES();

-- Table: editorial ranking, own periods and explicit simulated-vs-real separation.
SELECT analysis_date,DATEADD(day,-6,analysis_date) AS window_start,
       content_id,title,editorial_rank,valid_sessions,minutes_watched,
       avg_rating,rating_count,ratings_start,ratings_end,
       pageviews,views_start,views_end,
       best_observed_rank,first_observed_week,last_observed_week,netflix_status,
       sideflix_sessions_simulated,external_sources,published_at_utc
FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY
ORDER BY editorial_rank;

-- Run this query separately; in Chart choose bars, X=TITLE, Y=MINUTES_WATCHED.
-- Caption: simulated Sideflix viewing, window 26 Oct-1 Nov 2026;
-- events available only 30 Oct-1 Nov. External contexts are not Sideflix minutes.
SELECT title,minutes_watched
FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY
ORDER BY editorial_rank;

-- Independent daily acceptance check, Gold only: expected 13 /177.4 on 1 November.
SELECT usage_date,SUM(valid_sessions) AS sessions,SUM(minutes_watched) AS minutes
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY
WHERE usage_date='2026-11-01'::date GROUP BY usage_date;
-- Save screenshots of table, chart and context. A worksheet in one's workspace is private:
-- export the evidence for the jury; do not rely on an inaccessible Snowsight URL.

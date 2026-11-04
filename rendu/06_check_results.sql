-- Etape 6 : requetes de lecture pour verifier les transformations.
-- Executer avec SYSADMIN / SIDEFLIX_WH dans le compte du projet.
SELECT 'bronze_catalog' AS controle, COUNT(*)::VARCHAR AS obtenu
FROM SIDEFLIX.BRONZE.CATALOG
UNION ALL SELECT 'bronze_sessions', COUNT(*)::VARCHAR FROM SIDEFLIX.BRONZE.SESSIONS_RAW
UNION ALL SELECT 'silver_catalog', COUNT(*)::VARCHAR FROM SIDEFLIX.SILVER.SILVER_CATALOG
UNION ALL SELECT 'stg_sessions', COUNT(*)::VARCHAR FROM SIDEFLIX.SILVER.STG_SESSIONS
UNION ALL SELECT 'quarantine_sessions', COUNT(*)::VARCHAR FROM SIDEFLIX.SILVER.QUARANTINE_SESSIONS
UNION ALL SELECT 'silver_sessions', COUNT(*)::VARCHAR FROM SIDEFLIX.SILVER.SILVER_SESSIONS
UNION ALL SELECT 'reference_A', valid_sessions || ' sessions / ' || minutes_watched || ' minutes'
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY WHERE usage_date='2026-10-30' AND content_id='A'
UNION ALL SELECT 'reference_B', valid_sessions || ' sessions / ' || minutes_watched || ' minutes'
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY WHERE usage_date='2026-10-30' AND content_id='B'
UNION ALL SELECT 'rejet', session_id || ': ' || reject_reason
FROM SIDEFLIX.SILVER.QUARANTINE_SESSIONS;

-- Classement sur sept jours, date de demonstration explicite (donnees fixes).
SELECT g.content_id, c.title, SUM(g.valid_sessions) AS sessions_sur_7_jours,
       SUM(g.minutes_watched) AS minutes_sur_7_jours
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY g
JOIN SIDEFLIX.SILVER.SILVER_CATALOG c ON c.content_id=g.content_id
WHERE g.usage_date BETWEEN DATEADD(day, -6, '2026-11-01'::DATE) AND '2026-11-01'::DATE
GROUP BY g.content_id, c.title
ORDER BY minutes_sur_7_jours DESC, g.content_id;

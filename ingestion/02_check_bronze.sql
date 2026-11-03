-- Sideflix · Étape 5 : contrôle final de la couche Bronze après ingestion (un seul tableau).
-- Rôle SYSADMIN, warehouse SIDEFLIX_WH. Lecture seule : ne modifie rien.
-- Chaque ligne compare une valeur attendue (plan, étapes 3 et 5) à la valeur obtenue dans Snowflake.
USE ROLE SYSADMIN;
USE WAREHOUSE SIDEFLIX_WH;

WITH s AS (
    SELECT raw:session_id::STRING     AS session_id,
           raw:watched_seconds::NUMBER AS watched_seconds,
           _source_file
    FROM SIDEFLIX.BRONZE.SESSIONS_RAW
),
c AS (
    SELECT 'Catalogue : contenus en Bronze' AS controle, '6' AS attendu,
           TO_VARCHAR(COUNT(*)) AS obtenu FROM SIDEFLIX.BRONZE.CATALOG
    UNION ALL SELECT 'Catalogue : content_id distincts', '6',
           TO_VARCHAR(COUNT(DISTINCT content_id)) FROM SIDEFLIX.BRONZE.CATALOG
    UNION ALL SELECT 'Catalogue : titre de B mis a jour (5.2)', 'Dernier Metro (version restauree)',
           MAX(title) FROM SIDEFLIX.BRONZE.CATALOG WHERE content_id = 'B'
    UNION ALL SELECT 'LOAD_RUNS : executions journalisees', '3',
           TO_VARCHAR(COUNT(*)) FROM SIDEFLIX.BRONZE.LOAD_RUNS
    UNION ALL SELECT 'LOAD_RUNS : lignes extraites par run (ordre)', '6 / 0 / 1',
           LISTAGG(TO_VARCHAR(rows_extracted), ' / ') WITHIN GROUP (ORDER BY run_at) FROM SIDEFLIX.BRONZE.LOAD_RUNS
    UNION ALL SELECT 'Sessions : lignes brutes', '32', TO_VARCHAR(COUNT(*)) FROM s
    UNION ALL SELECT 'Sessions : fichiers sources', '3', TO_VARCHAR(COUNT(DISTINCT _source_file)) FROM s
    UNION ALL SELECT 'Sessions : session_id distincts', '31', TO_VARCHAR(COUNT(DISTINCT session_id)) FROM s
    UNION ALL SELECT 'Sessions : occurrences de S4 (doublon conserve)', '2',
           TO_VARCHAR(COUNT_IF(session_id = 'S4')) FROM s
    UNION ALL SELECT 'Sessions : duree de S31 (rejet attendu conserve)', '-60',
           TO_VARCHAR(MAX(IFF(session_id = 'S31', watched_seconds, NULL))) FROM s
)
SELECT controle, attendu, obtenu, IFF(attendu = obtenu, 'OK', 'ECART') AS verdict FROM c;

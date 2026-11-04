-- Initial Bronze objects: JSON format, internal landing stage, raw tables and run log.
-- Adapted from TD 2; run once as SYSADMIN before 04_bronze_v2_setup.sql.
-- Only creates absent objects; ingestion and dbt transformations are separate steps.
USE ROLE SYSADMIN;
USE WAREHOUSE SIDEFLIX_WH;
USE SCHEMA SIDEFLIX.BRONZE;

CREATE FILE FORMAT IF NOT EXISTS JSON_LINES
    TYPE = JSON
    STRIP_OUTER_ARRAY = FALSE
    COMMENT = 'Sideflix sessions: one JSON object per line';

CREATE STAGE IF NOT EXISTS SESSIONS_STAGE
    FILE_FORMAT = JSON_LINES
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Session file landing stage before COPY INTO SESSIONS_RAW';

CREATE TABLE IF NOT EXISTS SESSIONS_RAW (
    raw          VARIANT       COMMENT 'Raw session JSON object as received',
    _source_file VARCHAR       COMMENT 'Source filename (METADATA$FILENAME)',
    _loaded_at   TIMESTAMP_TZ  COMMENT 'Load timestamp'
)
COMMENT = 'Raw JSON sessions: duplicates and invalid values intentionally retained';

CREATE TABLE IF NOT EXISTS CATALOG (
    content_id       VARCHAR PRIMARY KEY,
    title            VARCHAR,
    content_type     VARCHAR,
    duration_seconds NUMBER,
    updated_at       TIMESTAMP_TZ  COMMENT 'Watermark cursor for incremental ingestion',
    _loaded_at       TIMESTAMP_TZ
)
COMMENT = 'Sideflix catalogue from PostgreSQL (updated_at watermark and MERGE)';

CREATE TABLE IF NOT EXISTS LOAD_RUNS (
    run_at          TIMESTAMP_TZ,
    watermark       VARCHAR,
    rows_extracted  NUMBER,
    rows_inserted   NUMBER,
    rows_updated    NUMBER,
    source_contents NUMBER        COMMENT 'PostgreSQL content count at run time',
    target_contents NUMBER        COMMENT 'Bronze content count after the run'
)
COMMENT = 'Catalogue incremental ingestion run journal';

SELECT 'TABLE' AS object_type, table_name AS name, table_owner AS owner, TO_VARCHAR(row_count) AS detail
FROM SIDEFLIX.INFORMATION_SCHEMA.TABLES WHERE table_schema = 'BRONZE'
UNION ALL
SELECT 'STAGE', stage_name, stage_owner, stage_type
FROM SIDEFLIX.INFORMATION_SCHEMA.STAGES WHERE stage_schema = 'BRONZE'
UNION ALL
SELECT 'FILE_FORMAT', file_format_name, file_format_owner, file_format_type
FROM SIDEFLIX.INFORMATION_SCHEMA.FILE_FORMATS WHERE file_format_schema = 'BRONZE'
ORDER BY object_type, name;

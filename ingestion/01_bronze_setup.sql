-- Sideflix · Action 4.3 : préparer la couche Bronze (format JSON, stage interne, tables).
-- Adaptation de 02_snowflake_setup.sql (TD 2, onprem-to-snowflake) :
--   * même rôle SYSADMIN, même principe IF NOT EXISTS (relance sans effet, rien n'est écrasé) ;
--   * format JSON au lieu du format CSV : les fichiers de sessions ont un objet JSON par ligne ;
--   * table brute SESSIONS_RAW en VARIANT (schema on read) : aucun nettoyage en Bronze,
--     le typage, la quarantaine et le dédoublonnage se feront dans Silver (dbt) ;
--   * table CATALOG = cible du MERGE incrémental (équivalent de ORDERS_INCR, TD 2 partie B) ;
--   * table LOAD_RUNS = journal des chargements du catalogue (équivalent de LOAD_RUNS, TD 2).
-- Hors périmètre (étape 5) : dépôt des fichiers sur le stage, COPY INTO, script MERGE.
-- Aucun objet REDGRAVE n'est lu ni modifié.
-- Exécution : Snowsight, rôle SYSADMIN choisi dans la feuille, tout sélectionner puis Run.

USE ROLE SYSADMIN;
USE WAREHOUSE SIDEFLIX_WH;
USE SCHEMA SIDEFLIX.BRONZE;

-- Format des fichiers de sessions : JSON, un objet par ligne (pas de tableau englobant).
CREATE FILE FORMAT IF NOT EXISTS JSON_LINES
    TYPE = JSON
    STRIP_OUTER_ARRAY = FALSE
    COMMENT = 'Sessions Sideflix : un objet JSON par ligne';

-- Stage interne : zone de dépôt des fichiers JSON avant COPY INTO (comme MERCH_STAGE au TD 2).
CREATE STAGE IF NOT EXISTS SESSIONS_STAGE
    FILE_FORMAT = JSON_LINES
    DIRECTORY = (ENABLE = TRUE)
    COMMENT = 'Depot des fichiers sessions_AAAA-MM-JJ.json avant COPY INTO SESSIONS_RAW';

-- Bronze sessions : une ligne JSON brute par ligne de fichier, plus la provenance.
CREATE TABLE IF NOT EXISTS SESSIONS_RAW (
    raw          VARIANT       COMMENT 'Objet JSON de la session, tel que recu',
    _source_file VARCHAR       COMMENT 'Fichier d origine (METADATA$FILENAME)',
    _loaded_at   TIMESTAMP_TZ  COMMENT 'Horodatage du chargement'
)
COMMENT = 'Sessions brutes (JSON) : doublons et valeurs invalides conserves volontairement';

-- Bronze catalogue : copie du catalogue PostgreSQL, mise à jour par MERGE sur content_id.
CREATE TABLE IF NOT EXISTS CATALOG (
    content_id       VARCHAR PRIMARY KEY,
    title            VARCHAR,
    content_type     VARCHAR,
    duration_seconds NUMBER,
    updated_at       TIMESTAMP_TZ  COMMENT 'Colonne curseur (watermark) de l ingestion incrementale',
    _loaded_at       TIMESTAMP_TZ
)
COMMENT = 'Catalogue Sideflix charge depuis PostgreSQL (watermark updated_at + MERGE)';

-- Journal des chargements du catalogue (un enregistrement par exécution du script).
CREATE TABLE IF NOT EXISTS LOAD_RUNS (
    run_at          TIMESTAMP_TZ,
    watermark       VARCHAR,
    rows_extracted  NUMBER,
    rows_inserted   NUMBER,
    rows_updated    NUMBER,
    source_contents NUMBER        COMMENT 'Nombre de contenus dans PostgreSQL au moment du run',
    target_contents NUMBER        COMMENT 'Nombre de contenus dans Bronze apres le run'
)
COMMENT = 'Journal des executions de l ingestion incrementale du catalogue';

-- Vérification (un seul tableau) : attendu 5 lignes, toutes détenues par SYSADMIN,
-- 3 tables vides (0 ligne), 1 stage INTERNAL, 1 format JSON.
SELECT 'TABLE' AS type_objet, table_name AS nom, table_owner AS proprietaire, TO_VARCHAR(row_count) AS detail
FROM SIDEFLIX.INFORMATION_SCHEMA.TABLES WHERE table_schema = 'BRONZE'
UNION ALL
SELECT 'STAGE', stage_name, stage_owner, stage_type
FROM SIDEFLIX.INFORMATION_SCHEMA.STAGES WHERE stage_schema = 'BRONZE'
UNION ALL
SELECT 'FILE_FORMAT', file_format_name, file_format_owner, file_format_type
FROM SIDEFLIX.INFORMATION_SCHEMA.FILE_FORMATS WHERE file_format_schema = 'BRONZE'
ORDER BY type_objet, nom;

-- Create the Sideflix database and Bronze/Silver/Gold/LAB schemas (TD 2).
-- Warehouse provisioning is managed separately by Terraform (TD 4.2).
-- Administrator bootstrap only; normal pipeline runs use SIDEFLIX_RUNNER.
-- IF NOT EXISTS preserves existing objects and data. No REDGRAVE objects are changed.
USE ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS SIDEFLIX
    COMMENT = 'Sideflix academic prototype: authentic external sources and simulated playback';

CREATE SCHEMA IF NOT EXISTS SIDEFLIX.BRONZE
    COMMENT = 'Raw PostgreSQL catalogue, JSON usage and public sources with load metadata';
CREATE SCHEMA IF NOT EXISTS SIDEFLIX.SILVER
    COMMENT = 'Cleaned, typed and deduplicated dbt data';
CREATE SCHEMA IF NOT EXISTS SIDEFLIX.GOLD
    COMMENT = 'Business metrics by content item and UTC day, built with dbt';
CREATE SCHEMA IF NOT EXISTS SIDEFLIX.LAB
    COMMENT = 'Operational checks and daily publication (DAILY_USAGE)';

SHOW SCHEMAS IN DATABASE SIDEFLIX;

SELECT CURRENT_REGION()                          AS snowflake_region,
       SPLIT_PART(SPLIT_PART(CURRENT_REGION(), '.', -1), '_', 1) AS cloud_provider,
       CURRENT_ROLE()                            AS active_role,
       CURRENT_VERSION()                         AS snowflake_version;

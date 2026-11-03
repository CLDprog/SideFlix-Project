-- Sideflix · Action 4.1 : créer la base SIDEFLIX et ses schémas dans Snowflake.
-- Adaptation de 02_snowflake_setup.sql (TD 2, onprem-to-snowflake) :
--   * même rôle SYSADMIN et même principe IF NOT EXISTS (relance sans effet) ;
--   * base SIDEFLIX au lieu de REDGRAVE, avec les quatre schémas du plan :
--     BRONZE (brut), SILVER et GOLD (dbt), LAB (contrôles et publication journalière).
-- Hors périmètre de 4.1 (volontairement absent) :
--   * le warehouse SIDEFLIX_WH, créé par Terraform à l'action 4.2 ;
--   * le format JSON, le stage et les tables Bronze, créés à l'action 4.3.
-- Aucun objet REDGRAVE n'est lu ni modifié. Aucun warehouse n'est nécessaire
-- pour créer une base et des schémas.
-- Exécution : Snowsight, nouvelle feuille SQL, coller ce fichier puis Run All.

USE ROLE SYSADMIN;

CREATE DATABASE IF NOT EXISTS SIDEFLIX
    COMMENT = 'Sideflix (projet scolaire, donnees fictives) - action 4.1';

CREATE SCHEMA IF NOT EXISTS SIDEFLIX.BRONZE
    COMMENT = 'Donnees brutes : catalogue PostgreSQL et sessions JSON, avec metadonnees de chargement';
CREATE SCHEMA IF NOT EXISTS SIDEFLIX.SILVER
    COMMENT = 'Donnees nettoyees, typees et dedoublonnees (dbt)';
CREATE SCHEMA IF NOT EXISTS SIDEFLIX.GOLD
    COMMENT = 'Indicateurs metier par contenu et par jour (dbt)';
CREATE SCHEMA IF NOT EXISTS SIDEFLIX.LAB
    COMMENT = 'Controles et publication journaliere (DAILY_USAGE)';

-- Vérification 1 : attendu BRONZE, GOLD, LAB, SILVER (+ INFORMATION_SCHEMA et PUBLIC,
-- créés automatiquement par Snowflake), tous détenus par SYSADMIN.
SHOW SCHEMAS IN DATABASE SIDEFLIX;

-- Vérification 2 : fournisseur cloud et région réellement utilisés par le compte.
-- CURRENT_REGION() renvoie par exemple AWS_US_WEST_2 (parfois préfixé PUBLIC.) :
-- le premier mot après l'éventuel préfixe est le fournisseur.
SELECT CURRENT_REGION()                          AS region_snowflake,
       SPLIT_PART(SPLIT_PART(CURRENT_REGION(), '.', -1), '_', 1) AS fournisseur_cloud,
       CURRENT_ROLE()                            AS role_utilise,
       CURRENT_VERSION()                         AS version_snowflake;

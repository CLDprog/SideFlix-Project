-- Jeremy only, ACCOUNTADMIN, after 10_admin_setup.sql (4 November 2026).
-- Dedicated service user for the Docker/Airflow jobs on the demonstration machine:
-- only SIDEFLIX_RUNNER, no secondary role, key-pair authentication only (no password).
-- Without it, the jobs on Jeremy's PC would run with an administrator user.
USE ROLE ACCOUNTADMIN;
CREATE USER IF NOT EXISTS SIDEFLIX_PIPELINE
  TYPE = SERVICE
  DEFAULT_ROLE = SIDEFLIX_RUNNER
  DEFAULT_WAREHOUSE = SIDEFLIX_WH
  DEFAULT_NAMESPACE = SIDEFLIX.BRONZE
  DEFAULT_SECONDARY_ROLES = ()
  COMMENT = 'Sideflix Airflow/Docker jobs, least privilege';
GRANT ROLE SIDEFLIX_RUNNER TO USER SIDEFLIX_PIPELINE;
-- Public key printed by gen_key.py (TD 2); the private key stays outside Git, mounted read-only.
ALTER USER SIDEFLIX_PIPELINE SET RSA_PUBLIC_KEY = '<PUBLIC_KEY_FROM_gen_key.py>';
DESC USER SIDEFLIX_PIPELINE;
SHOW GRANTS TO USER SIDEFLIX_PIPELINE;

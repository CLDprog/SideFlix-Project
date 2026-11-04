-- Jeremy only, ACCOUNTADMIN (4 November 2026). Rayan owns the consumption layer:
-- the Snowsight restitution built from Gold with the read-only analyst role.
USE ROLE ACCOUNTADMIN;
GRANT ROLE SIDEFLIX_ANALYST TO USER RAYAN_FAHER_BONNE;
-- Same protection as for Matis: no privileged secondary role leaking into his sessions.
ALTER USER RAYAN_FAHER_BONNE SET DEFAULT_SECONDARY_ROLES = ();
SHOW GRANTS TO USER RAYAN_FAHER_BONNE;

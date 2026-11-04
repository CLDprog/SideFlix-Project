# Group access to the Snowflake account

3 November 2026, Jérémy Caillaud's AI-assisted session. Purpose: let Matis and Rayan resume dbt steps 6/7 in the Snowflake account containing Sideflix without sharing Jérémy's private key or password.

## Initial setup and executed checks

Executed `ingestion/03_create_team_users.sql` in Snowsight as ACCOUNTADMIN: users MATIS_DOUAY and RAYAN_FAHER_BONNE, type PERSON, temporary password requiring a first-login change, default SYSADMIN, warehouse SIDEFLIX_WH, context SIDEFLIX.BRONZE; granted SYSADMIN to each. Temporary passwords were entered only in the executing Snowsight worksheet, shared privately and never stored in project files.

| Check | Expected | Observed | Evidence |
| --- | --- | --- | --- |
| MATIS_DOUAY role | USAGE on SYSADMIN, granted by ACCOUNTADMIN | Match | `rendu/snowflake_acces_groupe_show_grants.csv` |
| RAYAN_FAHER_BONNE role | USAGE on SYSADMIN, granted by ACCOUNTADMIN | Match | Same file |

Each member signs into Snowsight using the central Notion access instructions, changes the password and enables MFA if required. For Python/dbt, each generates their own RSA pair using lab 2 `gen_key.py`, sending **only the public key** to Jérémy for registration with `ALTER USER ... SET RSA_PUBLIC_KEY = '...'`.

Initial limitations: SYSADMIN exceeds least privilege (C7); limited roles were subsequently implemented and tested in step 10. Users depend on Jérémy's trial account, expected to end around 21 November 2026. Snowsight saves worksheets automatically, so entered temporary passwords must be cleared after execution.

## Matis's RSA registration, 4 November 2026

Step 5 scripts use the lab 2B RSA method (`connect_snowflake()` in `incremental_orders.py`). Each member keeps their own private key; private keys are never circulated.

1. Matis generated a pair with the original lab 2 `gen_key.py` in a local directory outside all repositories. Only the ALTER USER command containing the **public** key and expected fingerprint was posted to the step 5 Notion page.
2. Before execution, the fingerprint recalculated from the public key (SHA-256 of DER, base64 encoded) matched Matis's announcement; valid 2048-bit RSA. Both key slots in `DESC USER MATIS_DOUAY` were empty, so no existing key was overwritten.
3. At 14:49 UTC on 4 November, at Jérémy's request, his workstation executed `ALTER USER MATIS_DOUAY SET RSA_PUBLIC_KEY = '<Matis public key>'` as ACCOUNTADMIN through service-user key authentication, then DESC USER.

| Check | Expected | Observed | Evidence |
| --- | --- | --- | --- |
| Key slots before | Empty | null / null | `rendu/snowflake_cle_matis_verification.txt` |
| ALTER USER | Executed | Statement executed successfully | Same file |
| RSA_PUBLIC_KEY_FP after | `SHA256:CsUD4fP1ZdhtvytG5im9rjZNic8oH/J0e7ix3s4aFk8=` | Match | Same file |
| RSA_PUBLIC_KEY_2_FP after | Unchanged | null | Same file |

Required local variables are SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER=MATIS_DOUAY and SNOWFLAKE_PRIVATE_KEY_FILE. Registration alone did not prove the client connection; the actual check below did. Rotation/removal if needed: `ALTER USER MATIS_DOUAY UNSET RSA_PUBLIC_KEY;` as ACCOUNTADMIN.

## Actual Python connection, 4 November 2026

Reused the existing key without rotation. RSA connection succeeded: MATIS_DOUAY / SYSADMIN / SIDEFLIX_WH / SIDEFLIX.BRONZE. Before V2 ingestion: CATALOG=6, SESSIONS_RAW=32, LOAD_RUNS=3. Raw evidence: `python_connexion_matis.txt`.

The first system-connector 5.1.0 attempt was stopped by automatic review because cloud-platform detection tried 169.254.169.254. Correction: isolated `.venv`, pack connector 4.8.0, explicit SNOWFLAKE_JWT authentication and SNOWFLAKE_DISABLE_PLATFORM_DETECTION=true / AWS_EC2_METADATA_DISABLED=true. Connector code was inspected: this option exits detection before network calls. A local check returned disabled, then the full Snowflake connection passed. No instance credentials are required or used.

Variables and private key remain outside Git in local Sideflix-Local-Secrets. Reproducible dependencies: `ingestion/requirements.txt`; SQL session timezone UTC.

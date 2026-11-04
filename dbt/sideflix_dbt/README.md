# Sideflix dbt

Adapted from labs TD 3.2 and 3.3. Existing sources: SIDEFLIX.BRONZE.CATALOG and SESSIONS_RAW.

The provided profile is the one for **dbt Projects on Snowflake / Workspaces** (current session, no key or password). It does not work as is with dbt Core on a workstation or in Docker: there, use a local profile with variables and its own key, as in TD 3.1/4.2.

Silver: rebuilt views, Gold: rebuilt table. The log_run_results hook from the TD logs runs to SIDEFLIX.LAB.DBT_RESULTS. No changes to the Bronze sources.

Commands: `dbt run`, then `dbt docs generate`. Tests and their evidence will be completed in step 7, with `dbt build` then `dbt source freshness` separately.

October 30 reference: A = 2 sessions / 45 min; B = 1 session / 10 min. Overall: 32 raw rows = 30 valid sessions + 1 rejected + 1 duplicate removed.

## Final version v2 (November 4)

The verified batches are pinned in the `vars` of `dbt_project.yml`. The five public sources feed the Silver views, then `gold_editorial_weekly`, with periods, provenance, explicit Netflix absence and flagged simulation. Gold reads only from Silver. See `rendu/Etape_6_V2_Verifications.md` and `gold_editorial_v2.csv`.

Core: install `dbt/requirements.txt`, load the local Snowflake/RSA variables, export `SNOWFLAKE_DISABLE_PLATFORM_DETECTION=true AWS_EC2_METADATA_DISABLED=true DBT_SEND_ANONYMOUS_USAGE_STATS=false`, then from the root: `.venv/bin/dbt run --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core`. For Workspaces, use its existing profile. The Core profile embeds no key. The hook now distinguishes between the two runtimes.

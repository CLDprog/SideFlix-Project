# Step 6 V2 — dbt execution and result verification

4 November 2026, Matis. Prerequisite: step 5 V2 closed (`c74a961`), with five sources actually loaded and batches/replay checked.

## Implementation

Reused the existing dbt project: adapted five historical models, added five external Silver views and one editorial Gold table. Methods from labs 3.2/3.3 and pack 03: source/ref, TRY_TO_*, LATERAL FLATTEN, ROW_NUMBER/QUALIFY, quarantine and rebuilt Gold tables. No materialized view or Enterprise feature.

Secret-free Core/Docker profile: `dbt/profiles-core/profiles.yml`; the Workspaces profile remains separate. Executed versions: dbt Core 1.11.16 and Snowflake adapter 1.11.6 (pack Docker-runner versions), connector 4.8.0. Install `dbt/requirements.txt`. Export disabled platform detection before running dbt, as below.

Public and simulated batches are pinned explicitly in `dbt_project.yml` to the step 5 receipt. Refreshing them requires verifying the new receipt and updating those variables. Earlier sessions are excluded. The real catalog retains identity/provenance; each external Silver model retains source, batch, file and load time. Views do not modify Bronze.

Deduplication chooses the latest load (or source timestamp for ratings), then batch/file and stable row content. Sessions order by `_loaded_at DESC`, batch, file, source time and business fields; exact ties are equivalent. Duplicate S4 yields one session. Quarantine contains S31, -60 seconds, `invalid_watched_seconds`, RAW and metadata. Devices remain visible for the later incident's accepted_values test.

MovieLens ratings are aggregated by IMDb, pageviews by article and Netflix by confirmed content **before** joining to consumption metrics. The two unconfirmed Get Out observations remain in Silver without a match; only Sicario E is confirmed. Missing values remain NULL rather than fabricated zeros. Gold reads only Silver. Session days use UTC; scheduling uses Paris time separately.

## Observed results

- Successful dbt run/rebuild: 11 models + hook, PASS=12, WARN=0, ERROR=0. Deprecated-configuration warnings were subsequently cleaned up with the tests.
- Silver: IMDb 6; catalog 6; staging 32; quarantine 1; valid sessions 30; ratings aggregated for six works; Netflix three observations; Wikidata six works; Wikimedia 42 article/days.
- Daily Gold: 14 content/day rows, all compared with the independently calculated expected CSV. On 30 October: A=2 sessions/45 minutes; B=1/10; total 55 minutes.
- Editorial Gold: six works, 30 sessions and the same minutes total as daily Gold. All five sources contribute; ratings/metadata/pageviews exist for all six works, with one confirmed Netflix match. Whiplash ranks first: seven sessions and 112.666667 minutes. Ranking uses only simulated Sideflix metrics.
- External periods, Netflix status, simulation flag and `published_at_utc` are visible. There is no composite score. The timestamp records table construction; the subsequent build/tests validate publication.

## Commands and evidence

```sh
export SNOWFLAKE_DISABLE_PLATFORM_DETECTION=true AWS_EC2_METADATA_DISABLED=true DBT_SEND_ANONYMOUS_USAGE_STATS=false
.venv/bin/dbt run --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
.venv/bin/dbt docs generate --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
.venv/bin/python ingestion/verify_dbt_v2.py
```

Snowflake/RSA variables come from the private local configuration, never Git. Evidence: `dbt_6_v2_run.txt`, `dbt_6_v2_replay.txt`, `dbt_6_v2_docs.txt`, `dbt_6_v2_business_checks.txt`, `gold_editorial_v2.csv`. Generated dbt catalog/lineage files are in ignored `target/` and can be regenerated with the command above.

At this historical checkpoint, steps 7 and 8 were not validated. The Docker access test returned “permission denied while trying to connect to the docker API”, so no successful container execution was claimed here. **Update, 4 November:** steps 7 and 8 were subsequently completed; see `Etape_7_V2_Verifications.md` and `Etape_8_V2_Verifications.md`.

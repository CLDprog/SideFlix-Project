# Sideflix dbt

This project follows TD 3.2/3.3 and resource packs 03 and 07. Bronze sources are the PostgreSQL catalogue, simulated Sideflix sessions and five authentic public datasets: IMDb, MovieLens, Netflix Top 10, Wikidata and Wikimedia.

## Models and quality

Nine Silver views clean, type, quarantine and deduplicate inputs while retaining batch and provenance metadata. Two Gold tables provide daily usage and the editorial ranking. Each external source is aggregated to its intended grain before joining, preventing inflated session counts. The ranking uses simulated Sideflix minutes; historical external metrics provide separately dated context.

The demonstrated build has **11 models, 21 tests and one logging hook** (33 successful results). Freshness checks (warn after 24 h, error after 26 h) cover the catalogue and the selected session batch; they are measured from the ingestion journal `BRONZE.PUBLIC_SOURCE_RUNS`, because a replayed, unchanged batch keeps its first `_loaded_at`. Raw input contains 32 rows: 30 valid sessions, one rejected row and one duplicate. For 1 November 2026, daily Gold totals are **13 sessions and 177.4 minutes**. The seven-day window totals 30 sessions and 454.2 minutes.

## Run with dbt Core or Docker

In Docker, Airflow's `dbt_build` task runs the same two commands (`dbt source freshness`, then `dbt build`) in the `sideflix-dbt:1.0.0` image, with the batch IDs of the current ingestion receipt; see the launch procedure in the root README. To run them yourself:

From the repository root, use `dbt/profiles-core/profiles.yml`. Supply `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PRIVATE_KEY_FILE` and `SNOWFLAKE_ROLE=SIDEFLIX_RUNNER` through private environment variables. The runtime role is limited; it does not administer the account. Bronze and LAB tables must first be created with the setup scripts documented in the root README.

```sh
python -m pip install -r dbt/requirements.txt
dbt source freshness --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
dbt build --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
dbt docs generate --static --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
```

The default `vars` pin the reviewed source batches and analysis date. Airflow supplies the actual receipt batch IDs and selected date when it runs the same project. The `log_run_results` hook records each model/test result in `SIDEFLIX.LAB.DBT_RESULTS`.

`dbt docs generate --static` writes a self-contained `static_index.html` to the dbt target folder. To refresh the packaged documentation, copy it as `index.html`, with `manifest.json` and `catalog.json`, into `docs/dbt/` (see [docs/dbt/README.md](../../docs/dbt/README.md)).

For **dbt Projects on Snowflake / Workspaces only**, the separate `profiles.yml` in this directory follows the session-based course configuration. It is not a local dbt Core credential profile.

## Lineage and reliability

The generated dbt documentation (`docs/dbt/index.html`) includes source, model, column and test metadata. The architecture and lineage images are linked in the root README. The raw incident logs and evidence index show that invalid device data blocks Gold and publication, while retrying a crash after the publication write preserves one row per date.

An older prototype was preserved in LAB during development. Its historical verification is optional on a fresh installation and is separate from the required final-data checks.

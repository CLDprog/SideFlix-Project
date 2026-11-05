# Step 8 — launch following TD 4.2

*Internal project stage 8 (orchestration); in the root README it belongs to Framework steps 3 and 6. Stages 9.1 and 9.2 are the two incidents of Framework step 6.*

**Status as of 4 November 2026: actually run in Docker/Airflow on Jérémy's PC (Windows, Docker Desktop).** Demo run for 1 November and its replay succeeded, with a single publication per date; scheduled run for a day without data correctly failed, with retries and callback. Failure alert received on the group's Slack channel (8.4): step 8 complete. Evidence: `evidence/05_orchestration/orchestration_report.md`. Cloud/Core steps 5–7 are complete; do not redo them. No Terraform needed.

## On the demo machine

1. Open Docker Desktop and run `docker info` in the machine's terminal.
2. From the repository root, prepare the folders and the private file:

```sh
mkdir -p airflow/work airflow/state
cp airflow/.env.example airflow/.env
id -u
id -g
```

Fill in `.env`: Snowflake account/user, ABSOLUTE paths to the existing key, the repository and `airflow/work`, and `SIDEFLIX_TASK_USER=UID:GID` as returned above (on Windows: `1000:1000`, paths with `/`, for example `C:/Users/<user>/keys`). The `rsa_key.p8` key stays out of Git and is mounted read-only. Do not change its permissions to make the mount accessible: use the right UID.

The PG* variables in `.env.example` are ready: the source database is no longer a PostgreSQL instance to install on each machine, but the Compose `source-db` service (postgres:16.4, same method as `docker-compose-databases.yml` from pack 04, throwaway lab credentials, port 5433 restricted to localhost). On startup, the one-shot `catalog-seed` service loads the real catalog into it with `source/03_load_real_catalog.py` (idempotent). The DAG jobs reach it via `host.docker.internal:5433`. The raw source files are in `source/real/` (the group's private repository): nothing to download.

Set a **group Slack/Teams webhook** in `ALERT_WEBHOOK_URL`. Receipt on the group channel was confirmed on 4 November ([evidence/05_orchestration/airflow_8_4_slack_alert.txt](../evidence/05_orchestration/airflow_8_4_slack_alert.txt)). The callback comes from pack 07; a mere log line without a webhook is not evidence.

3. Build and start, from the root:

```sh
docker build -f docker/ingestion.Dockerfile -t sideflix-ingest:1.0.0 .
docker build -f docker/dbt.Dockerfile -t sideflix-dbt:1.0.0 .
docker compose -f airflow/docker-compose.yml up -d --build
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags list-import-errors
```

The Airflow container runs as root (the TD's exception for the Docker socket): go through `/entrypoint` for the CLI, as above.

Open http://localhost:8080 and unpause `sideflix_daily`. Airflow first starts the scheduled run for the previous day, which fails at `check_sources` by design (see below). Once it has failed, trigger `sideflix_daily` with the configuration **`{"date":"2026-11-01"}`**, then replay the same date. Keep the logs, duration, task states, publication checks and a secret-free copy of the results. Substeps 8.1–8.5 were validated on these actual runs, not on Python compilation or `compose config` alone.

The DAG reuses the TD's DockerOperator/Compose: real ingestion (catalog + five sources + sessions), batch/date check, freshness then dbt build, MERGE publication. UTC date and run_id passed to each task. Cron 06:00 Europe/Paris, retries=2, catchup=False, max_active_runs=1. Airflow is the only scheduler. The jobs are non-root; the Airflow container uses the TD's root exception for the Docker socket, exposed only on localhost.

## Demo and limitations

The snapshots are historical; the simulated sessions stop on 1 November. An automatic run requesting a missing day **fails**; no data for the day is invented. For the oral presentation, specify the date above. The ingestion image reuses the local snapshots mounted from `source/`; the APIs are actually called and the run receipt passes their new batch_id values to dbt without changing the versioned reference variables.

The `run_pipeline_job.py build` script writes a local marker only after freshness AND build have succeeded. `publish_daily_usage.py` requires this marker for the same date and run ID (it records the dbt invocation ID with the publication), reads Gold and runs a MERGE per date into SIDEFLIX.LAB.DAILY_USAGE. It rejects a missing day.

After step 8 was validated, incidents 9.1 (invalid device → test blocks → notification → fix) and 9.2 (`--crash-on-try 1` after MERGE, retry → one row per date) were actually run and recovered on 4 November 2026: Slack alert received for 9.1, corrective run 33/33, a single row per date after the 9.2 retry (evidence: `evidence/06_incidents/incident_report.md`). The last valid Gold is kept in case of an upstream failure. The timed demo runs take one to two minutes, well before 07:00 for a 06:00 trigger (`evidence/05_orchestration/airflow_8_v2_windows_runs.txt`); this is a local measurement on a single simulated day, and freshness thresholds alone do not prove it.

Good to know: as soon as the DAG is re-enabled, Airflow creates the scheduled run for the previous day (catchup disabled). Since the simulated sessions stop on 1 November, this run fails at the source check without publishing anything: this is the expected behavior, to be shown during the oral presentation.

Local shutdown: `docker compose -f airflow/docker-compose.yml down` (add `-v` to start over from an empty source database, reloaded on the next startup). The Snowflake account is a trial; do not recreate the Terraform objects or modify REDGRAVE.

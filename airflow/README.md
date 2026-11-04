# Step 8 — launch following TD 4.2

**Status as of November 4, 2026, 17:10: actually run in Docker/Airflow on Jérémy's PC (Windows, Docker Desktop).** Demo run for November 1 and its replay succeeded, with a single publication per date; scheduled run for a day without data correctly failed, with retries and callback. Failure alert received on the group's Slack channel (8.4): step 8 complete. Evidence: `rendu/Etape_8_V2_Verifications.md`. Cloud/Core steps 5–7 are complete; do not redo them. No Terraform needed.

## On the demo machine

1. Open Docker Desktop and run `docker info` in the machine's terminal. If only the assistant is blocked, run the Docker commands from that terminal.
2. From the repository root, prepare the folders and the private file:

```sh
mkdir -p airflow/work airflow/state
cp airflow/.env.example airflow/.env
id -u
id -g
```

Fill in `.env`: Snowflake account/user, ABSOLUTE paths to the existing key, the repository and `airflow/work`, and `SIDEFLIX_TASK_USER=UID:GID` as returned above (on Windows: `1000:1000`, paths with `/`, for example `C:/Users/vous/keys`). The `rsa_key.p8` key stays out of Git and is mounted read-only. Do not change its permissions to make the mount accessible: use the right UID.

The PG* variables in `.env.example` are ready: the source database is no longer a PostgreSQL instance to install on each machine, but the Compose `source-db` service (postgres:16.4, same method as `docker-compose-databases.yml` from pack 04, throwaway lab credentials, port 5433 restricted to localhost). On startup, the one-shot `catalog-seed` service loads the real catalog into it with `source/03_load_real_catalog.py` (idempotent). The DAG jobs reach it via `host.docker.internal:5433`. The raw source files are in `source/real/` (the group's private repository): nothing to download.

Set a **group Slack/Teams webhook** in `ALERT_WEBHOOK_URL`. No notification will be validated until the group has confirmed receiving it. The callback comes from pack 07; a mere log line without a webhook is not evidence.

3. Build and start, from the root:

```sh
docker build -f docker/ingestion.Dockerfile -t sideflix-ingest:1.0.0 .
docker build -f docker/dbt.Dockerfile -t sideflix-dbt:1.0.0 .
docker compose -f airflow/docker-compose.yml up -d --build
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags list-import-errors
```

The Airflow container runs as root (the TD's exception for the Docker socket): go through `/entrypoint` for the CLI, as above.

Open http://localhost:8080. Trigger `sideflix_daily` with the configuration **`{"date":"2026-11-01"}`**, then replay the same date. Keep the logs, duration, task states, publication checks and a secret-free copy of the results. Do not mark 8.1–8.4 as done based solely on Python compilation or `compose config`.

The DAG reuses the TD's DockerOperator/Compose: real ingestion (catalog + five sources + sessions), batch/date check, freshness then dbt build, MERGE publication. UTC date and run_id passed to each task. Cron 06:00 Europe/Paris, retries=2, catchup=False, max_active_runs=1. Airflow is the only scheduler. The jobs are non-root; the Airflow container uses the TD's root exception for the Docker socket, exposed only on localhost.

## Demo and limitations

The snapshots are historical; the simulated sessions stop on November 1. An automatic run requesting a missing day **fails**; no data for the day is invented. For the oral presentation, specify the date above. The ingestion image reuses the local snapshots mounted from `source/`; the APIs are actually called and the run receipt passes their new batch_id values to dbt without changing the versioned reference variables.

The `run_pipeline_job.py build` script writes a local marker only after freshness AND build have succeeded. `publish_daily_usage.py` requires this marker (matching date/run/invocation), reads Gold and runs a MERGE per date into SIDEFLIX.LAB.DAILY_USAGE. It rejects a missing day. The old fixture's target remains separate; do not mix the v2 tests into it.

Once step 8 is validated, continue with 9.1 (invalid device → test blocks → notification → fix) and 9.2 (`--crash-on-try 1` after MERGE, retry → one row per date). These incidents are not yet declared as executed. Keep the last valid Gold in case of an upstream failure. Check the 07:00 availability time with a timed run; freshness thresholds alone do not prove it.

Good to know: as soon as the DAG is re-enabled, Airflow creates the scheduled run for the previous day (catchup disabled). Since the simulated sessions stop on November 1, this run fails at the source check without publishing anything: this is the expected behavior, to be shown during the oral presentation.

Local shutdown: `docker compose -f airflow/docker-compose.yml down` (add `-v` to start over from an empty source database, reloaded on the next startup). The Snowflake account is a trial; do not recreate the Terraform objects or modify REDGRAVE.

# Step 8 V2 — Docker/Airflow execution and alert verification

**Completed on 4 November 2026 at 17:40 Paris time (Jérémy).** Docker/Airflow ran successfully on Jérémy's PC and the group Slack channel received an actual failure alert. Substeps 8.1–8.5 were validated. Earlier local preparation and access limitations are distinguished below.

## Implementation from lab 4.2 and packs 06/07

- `docker/ingestion.Dockerfile`, `docker/dbt.Dockerfile`: pack Python 3.12.7 base, pinned dependencies, non-root jobs, no copied secrets, `.dockerignore`.
- `airflow/docker-compose.yml`, `airflow/Dockerfile`, `airflow/dags/sideflix_daily.py`: lab standalone Airflow/DockerOperator. Ingest → source checks → freshness/build → publication. Cron at 06:00 Paris, two retries, catchup disabled, one active run; explicit UTC date/run_id. RSA mount is read-only; snapshots and receipts remain on the workstation.
- Adapted pack webhook callback; URL supplied through private runtime configuration, never Git.
- `ingestion/run_pipeline_job.py` reuses the collector, watermark/MERGE and loader. The receipt passes verified batches to dbt; publication requires successful build and freshness checks.
- `ingestion/publish_daily_usage.py` adapts the lab's publish_daily_sales: reads validated Gold and MERGEs by date into LAB.DAILY_USAGE. Its after-write crash option was prepared for step 9.2 and not triggered in this step.

Python compilation and static Compose checks passed but did not themselves validate images or the DAG. The initial local dbt-wrapper check could not resolve the executable because PATH omitted `.venv/bin`; this was fixed by resolving the executable in the same Python environment. Publication without a validation marker was correctly refused.

## Historical local prechecks and access limitation

Local Python/Core ingestion and source checks succeeded for six batches. The APIs were called again with identical batch hashes and no added rows. Freshness and parameterized dbt build passed 33/33. Publishing 30 October twice produced three sessions / 55 minutes and one row per date. The editorial reference date was then restored to 1 November. These are local prechecks, not container evidence.

An initial `docker info` from a restricted session returned `permission denied while trying to connect to the docker API at unix:///Users/matisdouay/.docker/run/docker.sock`. Socket/key permissions were not bypassed. Actual Docker execution later used Jérémy's workstation. No ACCOUNTADMIN or Terraform intervention was required for this step.

Historical precheck evidence:

- `docker_8_v2_access.txt`: actual daemon refusal.
- `docker_8_v2_compose_static.txt`: static configuration analysis without loading secrets.
- `pipeline_8_v2_local_ingest.txt`, `pipeline_8_v2_local_check.txt`, `pipeline_8_v2_local_build.txt`, `pipeline_8_v2_local_publish.txt`: local Python/Core checks.
- `pipeline_8_v2_restore_reference.txt`: editorial reference date restored after the parameterized-date check.

## Actual Docker/Airflow execution — Jérémy's PC, 4 November, 17:05–17:10 Paris

Docker Desktop on Windows with Docker Engine 29.9.2 (linux/amd64), lab standalone Airflow 3.3.2, following `airflow/README.md`.

### Portability corrections

- `source/real/` snapshots were shared in the private repository (`0577f62`, Matis). Windows Git line-ending conversion initially changed 14 of 19 file checksums although Git blobs were correct. `.gitattributes` disabled conversion for source data (`8cf1f97`); all 19 checksums then matched the manifest.
- Added Compose `source-db` (`postgres:16.4`, pack 04's database-container method, disposable lab credentials, port 5433 bound to localhost) and one-shot `catalog-seed` using the existing `source/03_load_real_catalog.py`: `CATALOGUE_OK rows=6 distinct_imdb=6 changed=6`. No separately installed PostgreSQL or personal database password is needed.
- Passed `PGPORT` to jobs and added `extra_hosts host.docker.internal` for portability beyond Docker Desktop.
- Fixed manual-run Jinja rendering. The original `dag_run.conf.get('date', data_interval_end...)` eagerly evaluated a default even when a date was supplied, while Airflow 3 manual runs have no data interval. A conditional now evaluates the fallback only when needed. Attempts 1 and 2 retain the template error; attempt 3 succeeded after correction.

### Results (evidence timestamps are UTC)

| Run | Processed day | Result | Duration | Verified log details |
| --- | --- | --- | --- | --- |
| `scheduled__2026-11-04T05:00:00+00:00`, automatically created when the DAG was enabled (06:00 Paris, catchup disabled) | 2026-11-03 | Expected failure | 1 min 35 s | Ingestion succeeded: six catalog timestamp updates from the new source container, unchanged values; six identical step 5 batches, zero added rows. `check_sources` failed on all three attempts: “No simulated sessions for requested UTC day”. Build/publication were upstream_failed, with nothing published. Callback: “ALERT NOT DELIVERED: missing ALERT_WEBHOOK_URL”. |
| `demo_20261101_run1`, manual `{"date":"2026-11-01"}` | 2026-11-01 | Success | 1 min 04 s for the successful attempt | Six batches with step 5 batch IDs; zero added rows/catalog extraction; `SOURCE_CHECKS_PASS`; freshness 2/2; build PASS=33 WARN=0 ERROR=0; `MERGE_PUBLISHED 2026-11-01 13 177.400000`. |
| `demo_20261101_run2_replay`, same date | 2026-11-01 | Success | 1 min 01 s | Same checks; no added rows; build 33/33; publication updated the same row. |

Independent Snowflake read after the runs: SIDEFLIX.LAB.DAILY_USAGE contains exactly one row for 1 November (13 sessions, 177.4 minutes, replay run_id), with no duplicate dates. This matches `source/v2/expected_daily_usage.csv`. Bronze volumes remain unchanged.

The 07:00 target is consistent with an approximately one-minute run scheduled at 06:00 Paris. This is a local measurement on one simulated day without contention, not a production SLA proof.

### Validated substeps

- 8.1: images `sideflix-ingest:1.0.0` and `sideflix-dbt:1.0.0` built and executed by Airflow; non-root jobs.
- 8.2: lab Compose started; `list-import-errors` returned no errors.
- 8.3: ingest → check → build → publish dependencies respected; checks block downstream tasks on failure.
- 8.5: MERGE publication retains one row per date after replay.
- 8.4: 06:00 Europe/Paris schedule, catchup disabled, one active run, three observed attempts (two retries), logs and actual Slack delivery verified below.

### Limitations and later follow-up

These step 8 runs used Jérémy's existing `REDGRAVE_AIRFLOW` user with SYSADMIN as then required by the scripts. Dedicated least-privilege execution was subsequently verified in step 10. Airflow itself runs as root for Docker socket access, following the lab exception. Simulated sessions end on 1 November; scheduled runs for absent dates intentionally fail.

The collector rewrites check timestamps in the mounted tracked files `source/sources_manifest.csv` and `source/catalog_real.csv`. Their values/checksums were checked (19/19) and timestamp-only changes restored after these runs. Moving those operational timestamps to `airflow/work` would avoid tracked-file changes.

Actual run evidence:

- `airflow_8_v2_windows_runs.txt`: versions, images, services, import check, scheduling, task states/times.
- `airflow_8_v2_windows_task_logs.txt`: attempt logs, corrected template error, batches, checks, build, publication and callback.
- `pipeline_8_v2_airflow_publication.txt`: independent read-only Snowflake verification.

## 8.4 — actual final failure delivered to Slack, 4 November, 17:31 Paris

Group channel `#sideflix-alertes`, application “Sideflix Airflow”, Incoming Webhook using pack 07's `on_failure_callback` with JSON `{"text": ...}`. Jérémy entered the URL in ignored `airflow/.env`; it is absent from tracked files and logs.

Actual failing manual run: `alert_test_20261103`, configuration `{"date":"2026-11-03"}`, a day without simulated sessions. Ingestion succeeded (six identical batches, no rows); `check_sources` failed on all three attempts. Build and publication were upstream_failed, so nothing was published. After the final attempt the callback logged `ALERT_DELIVERED_HTTP 200`.

Receipt was confirmed at 17:32 in the channel: Sideflix `sideflix_daily.check_sources` FAILED, run `alert_test_20261103`, attempt 3, with the local task-log link.

Evidence: `airflow_8_4_slack_alert.txt` (states and secret-free log excerpts) and `slack_8_4_alert_received.png` (received-message screenshot). Other group workstations configure their own private `airflow/.env` with the webhook, shared privately.

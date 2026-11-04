# Oral presentation and live demonstration runbook

Group 6 presents on **6 November 2026 at 13:00 Paris time**. The proposed speaking roles below must be agreed and rehearsed by all three members. This document does not claim a rehearsal has taken place. The exact speaking-time limit must be checked with the teacher; no duration is assumed here. Match these sections to the final versioned slide deck.

## Framework order and proposed speakers

| Framework step | Speaker proposed | Content and evidence |
| --- | --- | --- |
| 1. Company and use case | Matis | Explain the Sideflix fictional scenario and Netflix reference honestly. Catalogue manager, weekly feature-selection decision, assumptions, metric grain, formulas and exclusions. The Framework requests a real company: do not present Sideflix as a real company. |
| 2. Real sources | Matis | Five authentic datasets in `source/sources_manifest.csv`; real context is distinct from simulated Sideflix sessions. Explain dates, licences, identifiers and matching limits. |
| 3. Ingestion strategy | Matis | PostgreSQL watermark/MERGE, file stage/COPY, API requests/VARIANT; schema checks, landing storage, reconciliation, deduplication and quarantine. |
| 4. Cloud and tools | Jérémy | Executed architecture, AWS Snowflake, GCS for Terraform state only, local Docker/PostgreSQL/Airflow, justified choices, limited roles and measured costs. Disclose the auxiliary second cloud provider. |
| 5. Architecture and outcomes | Rayan | Gold table and chart in Snowsight, Whiplash first, business interpretation and limitations. Captures are in `rendu/Restitution_Snowsight.md`. Distinguish simulated viewing, historical ratings, page views and Netflix Top 10. |
| 6. Resilience, governance and live run | Jérémy and Matis | Execute the normal pipeline live, verify results and governance, inspect lineage and documentation, and show the two actually executed incidents and recoveries using the evidence below. |

## Before presenting

Use one active Airflow scheduler only. Keep the presentation workstation and Docker running, confirm Snowflake access and network connectivity, build the two images and start Compose using the README. Check that the DAG has no import errors. Use `SIDEFLIX_RUNNER` in the private Airflow configuration; never show `.env`, keys, passwords or webhook URLs.

Open Airflow, Snowsight, the architecture, lineage and evidence index in advance. The video and raw logs are fallbacks; they do not replace the required live pipeline execution.

## Execute and verify the normal run live

In Airflow, trigger `sideflix_daily` with a fresh run ID and this configuration:

```json
{"date":"2026-11-01"}
```

Do not set an `incident` option for the normal demonstration. Follow the current run rather than an older successful one. Show `ingest_sources`, `check_sources`, `dbt_build` and `publish_daily_usage` succeeding. Show `SOURCE_CHECKS_PASS`, the build summary (`PASS=33`, `ERROR=0`, including models and tests), and `PUBLICATION_UNIQUE_DATE_PASS`. Expected publication: **13 sessions and 177.4 minutes**, one row for the date. Explain the architecture or source choices while the run is executing.

Run these read-only checks in Snowsight under the runner role, with secondary roles disabled:

```sql
USE ROLE SIDEFLIX_RUNNER;
USE SECONDARY ROLES NONE;
USE WAREHOUSE SIDEFLIX_WH;
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();
SELECT SUM(valid_sessions) AS sessions, SUM(minutes_watched) AS minutes
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY
WHERE usage_date = '2026-11-01';
SELECT * FROM SIDEFLIX.LAB.DAILY_USAGE WHERE usage_date = '2026-11-01';
```

Check the date, totals, unique publication and current run identifier in the returned results. Then show the catalogue ranking using `docs/snowsight_rayan.sql`.

## Verify governance, lineage and documentation live

Use the analyst role with secondary roles disabled so an inherited administrator role cannot hide a permissions problem. Execute the following statements separately:

```sql
USE ROLE SIDEFLIX_ANALYST;
USE SECONDARY ROLES NONE;
USE WAREHOUSE SIDEFLIX_WH;
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();
SELECT * FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY LIMIT 3; -- must succeed
SELECT * FROM SIDEFLIX.BRONZE.SESSIONS_RAW LIMIT 1; -- must be denied
```

Explain the expected denial as evidence of isolation. No data is changed by these checks. The full executed allow/deny matrix, including denied writes, is in `rendu/Etape_10_access_tests.txt`; its prepared checks are in `governance/10_verify_access.sql`. Show the monitor and measured consumption from `rendu/Etape_10_V2_Verifications.md` without claiming a new measurement.

Open `docs/dbt_lineage.png` and the packaged dbt documentation using `docs/dbt/README.md` (serve the repository locally and browse `http://127.0.0.1:8001/docs/dbt/`). Trace one Bronze source through Silver to Gold, inspect the model descriptions and tests, and connect this lineage to the actual SQL models. Open the README launch procedure, `source/sources_manifest.csv`, and `rendu/INDEX_PREUVES.md` to demonstrate reproducibility, provenance and traceability. Confirm the docs correspond to the delivered models.

## Showcase both executed incidents and recovery

These are deliberate faults that were actually executed against the pipeline, with failed tasks and verified recoveries. They are not merely hypothetical scenarios. The Framework requires showcasing at least two real incident scenarios; present the execution evidence and recovery clearly. A fresh live normal run remains required separately.

| Scenario | Show the failure and protection | Show the recovery |
| --- | --- | --- |
| Invalid device category | `matis_9_1_bad_device`: isolated test batch; `accepted_values` fails after three attempts, Gold and publication remain unchanged, Slack alert received. Open `rendu/incident_9_1_logs/` and `rendu/incident_9_1_failed_and_cleanup.json`. | Only the identified test batch was removed; `matis_9_1_fixed` succeeds with build 33/33, 13 sessions / 177.4 minutes and no residual invalid session. Open `rendu/incident_9_1_recovery.json` and recovery logs. |
| Crash after publication write | `matis_9_2_crash`, attempt 1: the MERGE writes successfully, then the process deliberately crashes. Show `rendu/incident_9_2_after_first_write.json` and attempt 1 logs. | Airflow retries automatically; attempt 2 succeeds. `rendu/incident_9_2_recovered.json` and logs prove one row for the date with unchanged totals. Explain why MERGE prevents duplicate publication. |

The consolidated account is `rendu/Etape_9_V2_Verifications.md`. Replays `matis_9_replay1` and `matis_9_replay2` further prove stable values and no duplicate publication. Do not claim that these historical runs occurred during the oral. Do not improvise a destructive cleanup or run the invalid-device injection during the normal live demonstration.

## Final group checks

Agree the speakers and slide transitions, rehearse to the teacher's time limit, verify the workstation/network and professor's repository access, and identify each member's actual pipeline contribution. Rayan's assigned consumption section was executed and captured by Matis on 4 November; explain actual contributions accurately. Keep the normal-run video and evidence available as fallbacks.

# Execution evidence

This folder holds the optional execution evidence requested in Session 1.2: run IDs, dates, versions, results, checks, replay tests and screenshots. It was captured between 3 and 5 November 2026. Each folder covers one pipeline stage and opens with an English report that explains its raw files.

**How to read the raw files.** Logs, JSON receipts, CSV exports and screenshots keep their captured values. Some show French labels from the team's scripts, SQL aliases or exports: *attendu* = expected, *obtenu* = actual, *AUTORISE* = allowed, *REFUSE* = denied, *ligne(s)* = row(s), *contrôle* = check, *statut* = status, *contexte* = context, *lecture* = read, *facturation* = billing, *requetes* = queries, *en_erreur* = in error, *dates en double* = duplicate dates, *texte* = text, *verrou factice* = dummy lock. The Snowsight column aliases (RANG, TITRE, SESSIONS_VALIDES, MINUTES_REGARDEES, PUBLIE_UTC…) are French versions of the column names in `docs/snowsight_gold_report.sql`. On 5 November 2026 the human-written notes in some text logs (headers, section titles and inline annotations, never tool output) were translated into English. This folder was formerly named `rendu/`: SQL comments visible in the Snowsight screenshots still mention `rendu/`, and the Snowsight receipt names the former query file `docs/snowsight_rayan.sql` (now `docs/snowsight_gold_report.sql`).

## Folders

| Folder | Pipeline stage | Framework step · criteria | Start with |
| --- | --- | --- | --- |
| [01_sources](01_sources/) | Collection of the five authentic datasets, checksums and matching | 2 · C3 | [collection_report.md](01_sources/collection_report.md) |
| [02_ingestion](02_ingestion/) | PostgreSQL catalogue (watermark + MERGE), Bronze landing setup, file and API loads, exact replay | 3 · C3 | [ingestion_report.md](02_ingestion/ingestion_report.md) |
| [03_cloud_and_iac](03_cloud_and_iac/) | Snowflake region (AWS eu-west-3), Terraform init/plan/apply, migration to the GCS remote state, locking | 4 · C4, C5 | [terraform_report.md](03_cloud_and_iac/terraform_report.md) |
| [04_dbt_and_quality](04_dbt_and_quality/) | Silver and Gold models, 21 tests, freshness, reconciliation, independent business checks | 3, 6 · C3, C6 | [dbt_report.md](04_dbt_and_quality/dbt_report.md), [quality_report.md](04_dbt_and_quality/quality_report.md) |
| [05_orchestration](05_orchestration/) | Docker images, Airflow runs and replay, missing-day failure and Slack alert | 3, 6 · C3, C6 | [orchestration_report.md](05_orchestration/orchestration_report.md) |
| [06_incidents](06_incidents/) | Two executed incidents with recovery, their live rehearsal with the final code, two replays, missing-file procedure | 6 · C6 | [incident_report.md](06_incidents/incident_report.md) |
| [07_security_and_costs](07_security_and_costs/) | Limited roles, allowed/denied tests, service-user run, credits, projection, monitor | 4, 6 · C7 | [security_costs_report.md](07_security_and_costs/security_costs_report.md) |
| [08_gold_report](08_gold_report/) | Snowsight table, chart and daily check under the read-only analyst role | 5 · C2, C3 | [snowsight_report.md](08_gold_report/snowsight_report.md) |
| [09_video_run](09_video_run/) | Unmodified logs and completion receipt of the filmed Airflow run | 6 · C3 | [video_run_verification.json](09_video_run/video_run_verification.json) |
| [10_final_check](10_final_check/) | Rehearsal of the live sequence and final run of the delivered code, 5 November 2026 | 6 · C3, C5 | [final_check_verification.json](10_final_check/final_check_verification.json) |

## Grading criteria C1–C8

| Criterion | What is shown | Where |
| --- | --- | --- |
| C1 Convincing fictional company | Revenue model, customers, size, operations, stakeholders, problem and numerical constraints, explicit assumptions | [README, step 1](../README.md#step-1--company-and-use-case), slide 2 |
| C2 Use case and business value | Catalogue manager, weekly feature decision, grain, formulas, exclusions, daily cadence, acceptance test 13 sessions / 177.4 minutes | [README, step 1](../README.md#step-1--company-and-use-case), slides 3 and 11, [Gold report](08_gold_report/snowsight_report.md) |
| C3 Working end-to-end pipeline | Ingestion from three kinds of sources, Bronze/Silver/Gold models, Gold checked against the independent expected result, containerised Airflow jobs, documented launch | [02](02_ingestion/), [04](04_dbt_and_quality/), [05](05_orchestration/), [10](10_final_check/), [README launch procedure](../README.md#running-the-pipeline) |
| C4 Appropriate tools | Ingestion, storage and transformation choices, alternatives and trade-offs, measured small-data query (248 ms, 3 of 5 partitions) | [architecture](../docs/architecture.md), [step10_measurements.json](07_security_and_costs/step10_measurements.json) |
| C5 Actual, controlled cloud use | Snowflake on AWS actually traversed by every run, warehouse declared in Terraform, private, versioned and locked GCS state | [03](03_cloud_and_iac/), [Terraform README](../terraform/README.md) |
| C6 Reliability, quality, operations | Key, business-rule and freshness/completeness tests with a demonstrated failure; replay without double counting; schedule, retries, logs, two incidents with recovery | [04](04_dbt_and_quality/), [05](05_orchestration/), [06](06_incidents/) |
| C7 Security and costs | Allowed/denied access checks, protected keys and secrets, 1.44 credits measured, projection with assumptions, 10-credit monitor, shutdown procedure | [07](07_security_and_costs/), [governance README](../governance/README.md) |
| C8 Slides and presentation | English deck of 16 slides plus two appendix slides, with speaker notes; claims tied to this evidence, limitations stated, each member's contribution, slide plan with timing and speakers | [slides](../deliverables/Sideflix_Oral_Defense.pptx) ([PDF](../deliverables/Sideflix_Oral_Defense.pdf)), [live demonstration runbook](../docs/live_demo_runbook.md) |

## Key runs

| Run ID | Result | Evidence |
| --- | --- | --- |
| `demo_20261101_run1`, `demo_20261101_run2_replay` (Jérémy's PC) | dbt 33/33, 13 sessions / 177.4 minutes, then a replay without extra rows | [airflow_8_v2_windows_task_logs.txt](05_orchestration/airflow_8_v2_windows_task_logs.txt), [pipeline_8_v2_airflow_publication.txt](05_orchestration/pipeline_8_v2_airflow_publication.txt) |
| `alert_test_20261103` | Day without data blocked at `check_sources`; Slack notification received | [airflow_8_4_slack_alert.txt](05_orchestration/airflow_8_4_slack_alert.txt), [slack_8_4_alert_received.png](05_orchestration/slack_8_4_alert_received.png) |
| `matis_9_1_bad_device` → `matis_9_1_fixed` | `accepted_values` test fails, publication blocked, test batch removed, successful recovery | [incident_9_1_failed_and_cleanup.json](06_incidents/incident_9_1_failed_and_cleanup.json), [incident_9_1_recovery.json](06_incidents/incident_9_1_recovery.json), [failed-run logs](06_incidents/incident_9_1_logs/), [recovery logs](06_incidents/incident_9_1_recovery_logs/) |
| `matis_9_2_crash` | Write committed before the injected crash; retry succeeds; one publication row | [incident_9_2_after_first_write.json](06_incidents/incident_9_2_after_first_write.json), [incident_9_2_recovered.json](06_incidents/incident_9_2_recovered.json), [incident_9_2_logs](06_incidents/incident_9_2_logs/) |
| `matis_9_replay1`, `matis_9_replay2` | Same six batches, no new rows, unchanged business values | [incident_9_4_replay.json](06_incidents/incident_9_4_replay.json), [incident_9_4_logs](06_incidents/incident_9_4_logs/) |
| `live_rehearsal_9_2_crash`, `live_rehearsal_9_1_bad_device`, `live_rehearsal_9_1_recovery` (final code, 5 November) | 9.2: crash after MERGE then successful retry, one row; 9.1: test fails, publication blocked, Slack alert, 32 test rows deleted, recovery 33/33 | [receipt and key logs](06_incidents/live_rehearsal_20261105/rehearsal_receipt.json) |
| `runner_normal_20261101` (service user) | `SIDEFLIX_PIPELINE` with `SIDEFLIX_RUNNER`: 94 queries, 0 errors, dbt 33/33 | [runner_run.txt](07_security_and_costs/runner_run.txt) |
| `manual__2026-11-04T19:47:52.946628+00:00` (filmed, Matis's Mac) | Source checks pass, dbt 33/33, MERGE publishes 13 / 177.4, `PUBLICATION_UNIQUE_DATE_PASS` | [video](../deliverables/Sideflix_pipeline.mov), [receipt](09_video_run/video_run_verification.json), [logs](09_video_run/video_run_logs/) |
| `scheduled__2026-11-05T05:00:00+00:00` (rehearsal, Matis's Mac) | Started by unpausing the DAG; requests 4 November, fails at `check_sources` after 3 attempts by design, publishes nothing, Slack alert delivered | [receipt](10_final_check/final_check_verification.json), [logs](10_final_check/missing_day_logs/) |
| `final_verification_20261105` (final code, Matis's Mac) | 4 tasks succeed under `SIDEFLIX_RUNNER` (95 queries, 0 errors), freshness 2/2, dbt 33/33, 13 / 177.4 published once; Gold identical to the reference export | [receipt](10_final_check/final_check_verification.json), [logs](10_final_check/final_check_logs/) |

The incidents are **deliberately injected failures that were actually executed**, not spontaneous production outages. Reference data was preserved and the test injections were cleaned up.

## Recorded versions

Python 3.12.7 in the job images; Airflow 3.3.2; apache-airflow-providers-docker 4.5.9; dbt Core 1.11.16; dbt-snowflake 1.11.6; snowflake-connector-python 4.8.0; PostgreSQL 16.4; Terraform 1.16.6 with the snowflakedb/snowflake provider 2.22.1. Docker Engine: 29.9.2 on Jérémy's PC and 29.1.3 on Matis's Mac (final check).

## Limits

- The video ends while the publication task is still running; its successful completion is proved by the same run's logs in `09_video_run/`.
- The saved captures and runs prove recorded work. They do not replace the live run during the oral.
- The Gold screenshots were executed and captured by Matis for the consumption layer that Rayan owns and presents.

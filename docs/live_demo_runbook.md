# Oral presentation and live demonstration runbook

Group 6 presents on **6 November 2026 at 13:00 Paris time**. The proposed speaking roles below must be agreed and rehearsed by all three members. A technical rehearsal of the live sequence was run on 5 November ([evidence/10_final_check](../evidence/10_final_check/final_check_verification.json)); the speaking rehearsal is still to be done by the group. The exact speaking-time limit must be checked with the teacher; no speaking time is assumed here. Proposed slide plan: slides 1–8, 10 and 11 Matis; 9, 15, 16, 17 and 19 Jérémy; 13 Rayan; 12, 14 and 20 Jérémy and Matis, with Rayan presenting the Gold ranking during slide 20; 18 and 21 all three. The pipeline run itself takes about one minute (the final rehearsal run took 59 s), plus the scheduled run for the previous day that fails first (about 1 min 30 s) and the Snowsight checks.

## Framework order and proposed speakers

| Framework step | Speaker proposed | Content and evidence |
| --- | --- | --- |
| 1. Company and use case | Matis | Explain the Sideflix fictional scenario and Netflix reference honestly. Catalogue manager, weekly feature-selection decision, assumptions, metric grain, formulas and exclusions. The Framework requests a real company: do not present Sideflix as a real company. |
| 2. Real sources | Matis | Five authentic datasets in `source/sources_manifest.csv`; real context is distinct from simulated Sideflix sessions. Explain dates, licences, identifiers and matching limits. |
| 3. Ingestion strategy | Matis | PostgreSQL watermark/MERGE, file stage/COPY, API requests/VARIANT; schema checks, landing storage, reconciliation, deduplication and quarantine. |
| 4. Cloud and tools | Jérémy | Executed architecture, AWS Snowflake, GCS for Terraform state only, local Docker/PostgreSQL/Airflow, justified choices, limited roles and measured costs. Disclose the auxiliary second cloud provider. |
| 5. Architecture and outcomes | Rayan | Gold table and chart in Snowsight, Whiplash first, business interpretation and limitations. Captures are in `evidence/08_gold_report/snowsight_report.md`. Distinguish simulated viewing, historical ratings, page views and Netflix Top 10. |
| 6. Resilience, governance and live run | Jérémy and Matis | Execute the normal pipeline live, verify results and governance, inspect lineage and documentation, and run the two incidents live with their recovery (section below), keeping the recorded evidence as a fallback. |

## Before presenting

Use one active Airflow scheduler only. Keep the presentation workstation and Docker running, confirm Snowflake access and network connectivity, build the two images and start Compose using the README. Check that the DAG has no import errors. At least five minutes before presenting, unpause `sideflix_daily`: Airflow immediately starts the latest scheduled run, which targets the previous day. That day has no simulated sessions, so the run fails at `check_sources` by design, publishes nothing and sends one Slack alert; with `max_active_runs=1`, a manual run would wait behind it. Trigger the live run only after it has failed, and mention it as the missing-day guard if asked. Use `SIDEFLIX_RUNNER` in the private Airflow configuration; never show `.env`, keys, passwords or webhook URLs.

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

Check the date, totals, unique publication and current run identifier in the returned results. Rayan then presents the catalogue ranking under `SIDEFLIX_ANALYST` using `docs/snowsight_gold_report.sql` (from Matis's session unless `governance/10c_rayan_analyst.sql` has been run for Rayan's user).

## Verify governance, lineage and documentation live

Use the analyst role with secondary roles disabled so an inherited administrator role cannot hide a permissions problem. Execute the following statements separately:

```sql
USE ROLE SIDEFLIX_ANALYST;
USE SECONDARY ROLES NONE;
USE WAREHOUSE SIDEFLIX_WH;
SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_SECONDARY_ROLES();
SELECT * FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY LIMIT 3; -- must succeed
SELECT * FROM SIDEFLIX.BRONZE.SESSIONS_RAW LIMIT 1; -- must be denied
INSERT INTO SIDEFLIX.GOLD.GOLD_CONTENT_DAILY SELECT * FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY WHERE 1=0; -- must be denied (zero rows, changes nothing)
```

Explain the expected denials as evidence of isolation. No data is changed by these checks. The full executed allow/deny matrix, including denied writes, is in `evidence/07_security_and_costs/access_tests.txt`; its prepared checks are in `governance/10_verify_access.sql`. Show the monitor and measured consumption from `evidence/07_security_and_costs/security_costs_report.md` without claiming a new measurement.

Open the packaged dbt documentation, `docs/dbt/index.html`, directly in a browser (a self-contained static site, see `docs/dbt/README.md`); keep `docs/dbt_lineage.png` as the image fallback. Trace one Bronze source through Silver to Gold, inspect the model descriptions and tests, and connect this lineage to the actual SQL models. Open the README launch procedure, `source/sources_manifest.csv`, and `evidence/README.md` to demonstrate reproducibility, provenance and traceability. Confirm the docs correspond to the delivered models.

## Showcase the two incidents live, with recovery

Both incidents can be run live with the delivered code: they were rehearsed on 5 November (`live_rehearsal_9_2_crash`, `live_rehearsal_9_1_bad_device`, `live_rehearsal_9_1_recovery`, see `evidence/06_incidents/live_rehearsal_20261105/`). Run them after the normal run, each with a new run ID. If time is short, run incident 9.2 live and show incident 9.1 from its recorded evidence. The missing-day failure that starts when the DAG is unpaused is a third failure scenario seen live: the completeness check blocks the publication and alerts Slack.

| Incident | Trigger configuration | What the audience sees | Recovery |
| --- | --- | --- | --- |
| 9.2 — crash after the publication write (about 1 min 30 s, no cleanup) | `{"date":"2026-11-01","incident":"crash_after_write"}` | `publish_daily_usage` attempt 1 logs `MERGE_PUBLISHED`, then `Simulated crash AFTER write`; the task goes up for retry | Airflow retries after 20 s; attempt 2 publishes again and logs `PUBLICATION_UNIQUE_DATE_PASS`. `SIDEFLIX.LAB.DAILY_USAGE` still has one row for 1 November (13 sessions, 177.4 minutes), now with attempt 2: the MERGE prevents double counting |
| 9.1 — invalid device category (about 2 min, then cleanup) | `{"date":"2026-11-01","incident":"bad_device"}` | `ingest_sources` loads an isolated 32-row copy with one `invalid` device; `dbt_build` fails three times on `accepted_values` (`PASS=28 ERROR=1 SKIP=4`); `publish_daily_usage` is `upstream_failed`; Slack alert; Gold and the publication are unchanged | Run the prepared cleanup below, then trigger a normal run `{"date":"2026-11-01"}`: four green tasks, 13 sessions / 177.4 minutes, one row |

Prepared cleanup for 9.1, in Snowsight. The pipeline role has no DELETE right on Bronze by design, so the operator uses SYSADMIN and removes only the test batch:

```sql
USE ROLE SYSADMIN;
USE WAREHOUSE SIDEFLIX_WH;
-- Replace <run ID> with the run ID of the 9.1 run: expect one batch of 32 rows.
SELECT _batch_id, COUNT(*) FROM SIDEFLIX.BRONZE.SESSIONS_RAW
WHERE _batch_id IN (SELECT DISTINCT _batch_id FROM SIDEFLIX.BRONZE.SESSIONS_RAW
                    WHERE raw:incident_run_id::string = '<run ID>')
GROUP BY 1;
DELETE FROM SIDEFLIX.BRONZE.SESSIONS_RAW
WHERE _batch_id IN (SELECT DISTINCT _batch_id FROM SIDEFLIX.BRONZE.SESSIONS_RAW
                    WHERE raw:incident_run_id::string = '<run ID>');
```

Never add an `incident` option to the normal demonstration run, and use only the prepared cleanup statement. The first executions on 4 November remain the reference evidence: `matis_9_1_bad_device` → `matis_9_1_fixed` and `matis_9_2_crash`, consolidated in `evidence/06_incidents/incident_report.md`, plus the replays `matis_9_replay1` and `matis_9_replay2`.

## Final group checks

If the panel asks why there are so few sessions: the 32 sessions are a simulated demonstration and acceptance sample, built so that every rule can be checked by hand against an independent calculation; real viewing logs are private. At the assumed production volume (about 2,000 sessions per day for 10,000 subscribers), the same code runs unchanged, and a minimum number of sessions per title would be required before ranking.


Agree the speakers and slide transitions, rehearse to the teacher's time limit, verify the workstation/network and professor's repository access, and identify each member's actual pipeline contribution. Rayan's assigned consumption section was executed and captured by Matis on 4 November; explain actual contributions accurately. Keep the normal-run video and evidence available as fallbacks. After the live run, `ingest_sources` will have rewritten the check timestamps in `source/sources_manifest.csv` and `source/catalog_real.csv`; once checksums and business values are confirmed unchanged, discard these timestamp-only changes instead of committing them.

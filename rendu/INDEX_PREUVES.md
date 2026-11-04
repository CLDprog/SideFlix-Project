# Final evidence index

Evidence captured on 4 November 2026. Raw logs, screenshots and query receipts are retained without translation or modification; English reports explain them. Historical prototype reports and duplicate fixtures have been removed from the submitted tree. This index proves recorded work, not a future oral demonstration or the teacher's access to the private repository.

## Framework order and C1–C8

| Framework step / criterion | Implemented work | Evidence |
| --- | --- | --- |
| 1. Company and use case — C1/C2 | Fictional independent-streaming company; real Netflix industry anchor; catalogue manager chooses weekly featured content from valid sessions/minutes, refreshed daily | [README](../README.md), [English slides](../deliverables/Sideflix_Oral_Defense.pptx), [sources and scope](../docs/sources_and_catalogue.md) |
| 2. At least five authentic datasets — C3 | IMDb, MovieLens, Netflix Top 10, Wikidata, Wikimedia; identifiers, grain, periods, conditions, file hashes; simulated sessions excluded from authentic-source count | `source/sources_manifest.csv`, `source/content_mapping.csv`, [collection verification](Collecte_V2_Verifications.md) |
| 3. Different ingestion methods — C3 | PostgreSQL watermark/MERGE; files PUT/stage/COPY; API requests/VARIANT; batch identifiers and error handling | `ingestion/`, [ingestion report](Etape_5_V2_Verifications.md), `python_5_v2_catalog_initial.txt`, `python_5_v2_catalog_replay.txt`, `python_5_v2_sources_initial.txt`, `python_5_v2_sources_replay.txt`, `ingestion_v2_initial.json`, `ingestion_v2_replay.json` |
| 4. Justified tools/cloud — C4/C5 | Snowflake on AWS Paris; local PostgreSQL/Docker/Airflow; X-Small warehouse as Terraform code; GCS for state only, private/versioned/locked | [architecture](../docs/architecture_v2.md), [Terraform](../terraform/README.md), [state evidence](Etape_4_2_V2_Verifications.md), `terraform_4_2_v2_migration_gcs.txt`, `terraform_4_2_plan_after_apply.txt` |
| 5. Business slides and full architecture — C2/C8 | 21-slide English deck, all components/data flows, Gold use case and chart | [slides](../deliverables/Sideflix_Oral_Defense.pptx), [diagram](../docs/architecture_v2.png), [Snowsight](Restitution_Snowsight.md) |
| 6. Two real executed incidents and recovery — C6 | Actual controlled invalid-device failure/recovery; actual post-write crash/retry with no duplicate publication | [incident report](Etape_9_V2_Verifications.md), [incident 1 failure](incident_9_1_failed_and_cleanup.json), [incident 1 recovery](incident_9_1_recovery.json), [incident 2 first write](incident_9_2_after_first_write.json), [incident 2 retry](incident_9_2_recovered.json), `incident_9_1_logs/`, `incident_9_1_recovery_logs/`, `incident_9_2_logs/` |
| 6. Live run, governance, lineage, documentation — C3/C6/C7/C8 | Pipeline runnable; live sequence includes allowed/denied role checks, lineage and model documentation | [oral runbook](../docs/conducteur_oral.md), [policy SQL](../governance/10_verify_access.sql), [dbt documentation](../docs/dbt/README.md), [lineage](../docs/dbt_lineage.png). **Must still be executed during the oral.** |
| Proportionate architecture/performance — C4 | Batch decision cadence, alternatives explained, no unnecessary streaming/clustering; actual small-data query measurement | [architecture alternatives](../docs/architecture_v2.md), `Etape_10_Mesures.json`: 248 ms elapsed, 3,072 bytes, 3/5 partitions, result cache disabled but data cache 100% |
| Quality, reconciliation and replay — C2/C3/C6 | 11 dbt models, 21 tests, one audit hook; 33 successes; freshness 2/2; 32 raw = 30 valid + 1 quarantine + 1 duplicate; expected Gold independently checked | [dbt report](Etape_6_V2_Verifications.md), [quality report](Etape_7_V2_Verifications.md), `dbt_7_v2_build.txt`, `dbt_7_v2_freshness.txt`, `dbt_7_v2_run_results.json`, `dbt_6_v2_business_checks.txt`, `incident_9_4_replay.json` |
| Access, secrets and costs — C7 | SIDEFLIX_RUNNER service role, Gold-only analyst, recorded denials; RSA runtime keys; real metering plus labelled projection; 10-credit monthly monitor | [governance report](Etape_10_V2_Verifications.md), `Etape_10_access_tests.txt`, `Etape_10_admin_outputs.txt`, `Etape_10_runner_run.txt`, [operating procedure](../governance/README.md) |
| Contributions — C8 | Actual contributions recorded; Rayan assigned the Gold consumption layer, not falsely credited for Matis's captures | [README contributions](../README.md), [oral runbook](../docs/conducteur_oral.md), [Snowsight attribution](Restitution_Snowsight.md), Git history |

## Key runs and results

| Run | Result | Evidence |
| --- | --- | --- |
| `demo_20261101_run1` / `demo_20261101_run2_replay` — Jérémy | 33/33, 13 sessions / 177.4 minutes, then replay without extra rows | `airflow_8_v2_windows_task_logs.txt`, `pipeline_8_v2_airflow_publication.txt` |
| `alert_test_20261103` | Missing date blocked; actual Slack notification | `airflow_8_4_alerte_slack.txt`, `slack_8_4_alerte_recue.png` |
| `matis_9_1_bad_device` → `matis_9_1_fixed` | Accepted-values test fails; downstream publication blocked; targeted removal and successful recovery | `incident_9_1_failed_and_cleanup.json`, `incident_9_1_recovery.json`, task logs |
| `matis_9_2_crash` | First write committed before injected failure; second attempt succeeds; one publication row | `incident_9_2_after_first_write.json`, `incident_9_2_recovered.json`, `incident_9_2_logs/` |
| `matis_9_replay1`, `matis_9_replay2` | Same six batches, no new rows, stable business values | `incident_9_4_replay.json`, `incident_9_4_logs/` |
| `runner_normal_20261101` — Jérémy | Restricted runner: 94 queries, 0 errors, dbt 33/33 | `Etape_10_runner_run.txt` |
| `manual__2026-11-04T19:47:52.946628+00:00` — filmed on Matis's Mac | Source checks pass; dbt 33/33; MERGE publishes 13 / 177.4; `PUBLICATION_UNIQUE_DATE_PASS` | [video](../deliverables/Sideflix_pipeline.mov), [actual final-task receipt](video_run_verification.json), [unmodified task logs](video_run_logs/) |

The incidents are **deliberately injected failures actually executed**, not spontaneous production outages. Reference data was preserved and test injections were cleaned up. Do not inject an incident into the normal video/live run by accident.

## Gold consumption and dbt documentation

- [Snowsight report](Restitution_Snowsight.md): actual screenshots under SIDEFLIX_ANALYST with secondary roles disabled; six ranked films and dated source context.
- `Restitution_SQL_Verification.json` preserves original SQL, query IDs, user, role and results. New English aliases in `docs/snowsight_rayan.sql` change presentation labels only; they do not rewrite this historical receipt.
- Expected: 1 November 13 sessions / 177.4 minutes; all three days 30 / 454.2; Whiplash weekly first with 7 / 112.7.
- [Browsable dbt documentation](../docs/dbt/README.md), [model YAML](../dbt/sideflix_dbt/models/), [lineage PNG](../docs/dbt_lineage.png). Documentation is a captured catalog, not a fresh database execution.

## Recorded versions

Python 3.12.7 in job images; Airflow 3.3.2; apache-airflow-providers-docker 4.5.9; dbt Core 1.11.16; dbt-snowflake 1.11.6; snowflake-connector-python 4.8.0; PostgreSQL 16.4; Terraform 1.16.6 with snowflakedb/snowflake 2.22.1. Docker recorded on Jérémy's machine: 29.9.2; Matis: 29.3.1. These are evidence versions, not a claim that the final audit reran those systems.

## Final delivery checks and honest limits

Teacher instructions: Session 1.2 p.6 requires slides, architecture, Git with README, and the pipeline video (not graded); separate execution evidence is optional. Session 4.2 p.39 requests multiple sources/methods, “1 cloud”, ownership by each member and dbt documentation. Framework p.6 requires two executed incident/recovery demonstrations and a real pipeline run during the presentation with governance, lineage and documentation checks.

The rubric C1 and Framework differ on fictional/real company: Sideflix is fictional with Netflix as a real-world reference. AWS handles data/compute; GCS stores state only, so a single-provider interpretation is not claimed. The saved video ends during publication, whose actual successful completion is separately proved. Each member must explain their own work at the oral.

[Final audit](../docs/DELIVERY_AUDIT.md) records corrections, static checks and items requiring the presenters/account owner. Teacher access, successful remote push, platform submission and the future oral are not marked complete without evidence.

# Step 7 V2 — tests and business verification

4 November 2026, Matis. Steps 5 and 6 V2 were checked and closed before this step.

## Executed tests

`dbt build`: **PASS=33, WARN=0, ERROR=0, SKIP=0**, covering 11 models, 21 tests and a hook. Checks include unique/non-null keys, content/session relationships, allowed types/devices, durations, external grains, pageview periods, coverage of five datasets, reconciliation 32=30+1+1, Silver/Gold equality and no inflation after enrichment. Tests use the labs' methods and the pack's singular SQL tests, with no additional test package.

Separately executed `dbt source freshness`: **2/2 PASS**, for the catalog and simulated V2 session batch. Thresholds: warning after 24 hours and error after 26 hours for a daily flow. These detect stale loads; alone they do not prove the 07:00 deadline. Airflow scheduling/runtime evidence is in step 8. A catalog may legitimately remain unchanged during replay; for a fixed-date simulation, batches and the manifest remain the reference checks. **Update, 5 November:** freshness is now measured from the ingestion journal `BRONZE.PUBLIC_SOURCE_RUNS` (dbt `loaded_at_query`, same thresholds), because a replayed batch keeps its first `_loaded_at` and every replay more than 26 hours after the load would otherwise fail ([final run](../10_final_check/final_check_verification.json)).

The five public snapshots are not labeled “fresh” based on their historical business dates. Presence, expected batches, checksums and volumes are checked. MovieLens ratings span 1996–2018; Netflix Sicario was observed on 9 March 2025; Wikimedia covers 26 October–1 November 2026. A missing/emptied required source or incorrect observation count fails `assert_public_completeness`. Every model it reads is upstream of `GOLD_EDITORIAL_WEEKLY`, so a failure skips that table and fails the build, which blocks the publication; `GOLD_CONTENT_DAILY` does not wait for this test.

## Independent comparisons

`ingestion/verify_business_samples.py` uses source files, actual API responses and LAB reference tables:

| Sample | Independently recalculated expectation | Cloud observation |
| --- | --- | --- |
| Isolated LAB fixture, 30 October | 32 raw = 30 valid + one rejection + one duplicate; A 45 min + B 10 min | A 2/45, B 1/10: three sessions / 55 min |
| Final A batch, 31 October | Three distinct session_id values; 2,610 seconds / 60 | Three sessions / 43.5 min |
| MovieLens Whiplash | 38 ratings, total 153.5, average 4.0394736842 | 38 / 4.0394736842 |
| Wikimedia Whiplash | Sum of the seven received days: 15,551 | 15,551 |
| Netflix Sicario | 9 March 2025, rank 5, one matched observation | 9 March 2025, rank 5, one observation |

All 14 content/day results were also compared against the independent CSV in step 6. The editorial table's six works retain identical consumption totals, with periods and simulated provenance visible.

## Evidence and reproduction

With private local variables and the step 6 dbt environment:

```sh
.venv/bin/dbt build --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
.venv/bin/dbt source freshness --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
.venv/bin/python ingestion/verify_business_samples.py
```

Evidence: `dbt_7_v2_build.txt`, `dbt_7_v2_run_results.json`, `dbt_7_v2_freshness.txt`, `dbt_7_v2_freshness_results.json`, `dbt_7_v2_business_samples.txt`. Source/ref lineage and documentation were generated with `dbt docs generate` and are packaged in `docs/dbt/`. Initial YAML/config warnings were cleaned up.

Step 7's reference checks are complete. The blocking behaviour was then exercised for real: the invalid-device injection, blocked publication and recovery are incident 9.1 in [incident_report.md](../06_incidents/incident_report.md), and the scheduled Airflow runs are in [orchestration_report.md](../05_orchestration/orchestration_report.md).

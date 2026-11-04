# Step 9 V2 — two actual incidents, recovery and stable replay

**Completed on 4 November 2026: 9.1, 9.2, 9.3 and 9.4 verified.** Both incidents were actually executed and recovered, the quality alert was received, and two subsequent normal runs were stable. Step 8 was checked against Jérémy's evidence (`3106d9f`).

## Preparation and isolation

Matis started Docker from his own terminal (engine 29.3.1); the assistant did not bypass Docker-socket permissions. A read-only local Airflow check found `sideflix_daily`, paused, with no import errors. The CLI's “No data found” did not mean the DAG file was absent. Private Mac configuration was prepared and webhook presence checked without exposing its value.

The initial Snowflake state is captured in `incident_9_v2_before.json`: daily Gold, editorial Gold and the 1 November publication. That check changed no data.

The normal DAG is unchanged unless the manual run supplies `incident`. Options use lab 3.2/4.2 methods:

- **9.1:** `{"date":"2026-11-01","incident":"bad_device"}` creates an in-memory copy of 32 sessions, replacing S1 with TEST_BAD_DEVICE/device=invalid. The same PUT/COPY path loads a distinct batch. Row counts/durations stay unchanged so the intended accepted_values test, rather than an earlier completeness check, detects the fault. The run_id distinguishes the test batch; retries reuse it. The receipt selects this copy without changing reference snapshots.
- **9.1 recovery:** after the failed run/retries finish, remove only the batch identified by its exact batch_id and launch a new normal run to select the original sessions. No unrelated batch is deleted.
- **9.2:** `{"date":"2026-11-01","incident":"crash_after_write"}` passes `--crash-on-try 1` to the publication script, as in lab 4.2. First publication fails after MERGE; automatic retry succeeds with one row/date. This was executed after 9.1 recovery.
- **9.3:** a documented missing-file procedure, not a claimed third executed incident.
- **9.4:** two normal runs with stable results and no active injection.

Generated landing files are ignored by Git. Timestamp-only changes to manifest/catalog files are discarded after comparing checksums and business values.

## 9.1 — invalid device, blocked publication and verified recovery

Actual run `matis_9_1_bad_device`, Mac Docker/Airflow, 4 November. Ingestion and `check_sources` succeeded. All three `dbt_build` attempts failed exclusively on `accepted_values_silver_sessions_device__web__mobile__tv` (one invalid value): PASS=28, ERROR=1, SKIP=4. Both Gold tables and their tests were skipped; publication was upstream_failed with attempt 0. After the final failure, the callback logged `ALERT_DELIVERED_HTTP 200`.

A full Snowflake comparison against `incident_9_v2_before.json` showed daily Gold, editorial Gold (including timestamps) and the 1 November publication strictly unchanged. TEST_BAD_DEVICE/invalid was observed in Silver exclusively from test batch `sessions_simulated_96d78fad181a1ed6db07727b`.

After the run and retries finished, targeted cleanup deleted only the 32-row demonstration batch from Bronze. The original 32-row batch and reference files were preserved. All 19 manifest checksums remained valid. Collector timestamp-only changes were restored after comparing every other value. The ingestion journal retains the test batch as historical evidence; the faulty data copy was removed.

Matis confirmed receiving the dbt_build attempt-3 Slack alert at 18:13 Paris (`incident_9_1_slack_confirmation.txt`). Corrective run `matis_9_1_fixed`, without `incident`, succeeded on all four tasks: PASS=33/WARN=0/ERROR=0/SKIP=0. Actual Snowflake checks confirmed:

- One publication for 1 November: 13 sessions / 177.4 minutes, corrective run_id.
- 30 unique Silver sessions, no TEST_BAD_DEVICE or invalid device, no residual test batch.
- All 14 daily Gold rows identical to the pre-incident values.
- Six editorial works and 30 total sessions.
- All 19 source checksums conformant; timestamp-only changes restored.

Cause: an out-of-contract device category in an isolated copy. Avoided impact: publishing unvalidated data. Detection: accepted_values failure, Airflow retries exhausted, delivered alert. Recovery: remove only the faulty copy and run normally. Prevention: blocking test before Gold/publication, injection disabled by default.

Evidence: `incident_9_1_logs/`, `incident_9_1_failed_and_cleanup.json`, `incident_9_v2_before.json`, `incident_9_1_slack_confirmation.txt`, `incident_9_1_recovery.json`, `incident_9_1_recovery_logs/`.

## 9.2 — actual after-write crash and automatic retry

Run `matis_9_2_crash`, 4 November, `incident=crash_after_write`. Ingestion, source checks and dbt succeeded. Publication attempt 1 logged `MERGE_PUBLISHED 2026-11-01 13 177.400000`, then `Simulated crash AFTER write (TD4.2)`.

During up_for_retry, an actual Snowflake read found exactly one row with the same 13 sessions / 177.4 minutes, current run_id and attempt 1. Automatic attempt 2 succeeded and logged `PUBLICATION_UNIQUE_DATE_PASS`; the complete DAG finished success.

An independent final check still found one row for 1 November, 13 sessions / 177.4 minutes, attempt 2; no duplicate DAILY_USAGE dates; 30 Silver sessions; no residual anomaly; 19/19 source checksums conformant. The first write was not added a second time. An additive INSERT would have created another row; MERGE on usage_date updates the existing one. No final-failure alert is expected because retry recovered successfully.

Cause: intentionally failing after the write committed but before success confirmation. Potential impact: repeating a write after lost confirmation. Detection: failed first Airflow attempt and explicit logs. Recovery: automatic retry. Prevention: idempotent date-based MERGE and duplicate checks. Crash injection applies only to the configured run.

Evidence: `incident_9_2_after_first_write.json`, `incident_9_2_recovered.json`, `incident_9_2_logs/` (two publication attempts and upstream tasks).

## 9.3 — documented missing-file procedure

`Procedure_9_3_Fichier_Manquant.md` documents restoring only the affected file, verifying its checksum, rerunning the same date and checking values/publication. The collector may download some missing files again; otherwise failure occurs in ingestion or source checks for an incomplete batch. Both block publication. No third executed simulation is claimed.

## 9.4 — two normal runs and closure

On 4 November, `matis_9_replay1` (18:42–18:43 Paris) and `matis_9_replay2` (18:43–18:44 Paris) both succeeded: four tasks success, one attempt each, dbt PASS=33/WARN=0/ERROR=0/SKIP=0. Snowflake's journal records 11 successful models and 21 passing tests per invocation.

The two receipts are identical: the same six batch IDs, expected volumes 32/6/86/3/6/6, zero added rows in every batch. Files and API responses therefore represent the same snapshot despite actual repeated API calls. Both publication logs show 13 sessions / 177.4 minutes and `PUBLICATION_UNIQUE_DATE_PASS`.

The final SQL check found one publication for 1 November, second replay run_id, attempt 1, with no duplicate dates. All 14 daily Gold rows and six editorial rows, including external context, match the verified post-9.2 result, apart from the normally changing publication timestamp. Silver has 30 unique sessions, one rejection, no TEST_BAD_DEVICE or invalid device. Batch volumes and all 19 checksums remain unchanged. Collector timestamps were restored without changing other values.

Per-run evidence comes from logs, receipts, validation markers and dbt results. The independent SQL read confirms the final state; it is not claimed to have been taken between the two replays. Evidence: `incident_9_4_replay.json`, `incident_9_4_logs/`.

No injection was active in these normal runs. The demonstration configuration is `{"date":"2026-11-01"}` with a new run_id and no incident key. Docker/the workstation must remain running. The simulated data ends on 1 November; an absent date intentionally fails. Step 9 is complete; governance/security/costs are documented in step 10.

# Step 10 — governance, costs and operations verified

**Completed on 4 November 2026.** Jérémy performed and verified administrative setup by 19:20 Paris: limited roles, actual denied operations, a normal Airflow run under SIDEFLIX_RUNNER with a dedicated service user, attached resource monitor, observed credits and storage. He enabled monitor email notifications in his Snowsight profile at 19:50. Steps 1–9 were already verified. No Terraform command or REDGRAVE change was performed in this step.

## 10.1 — security and governance

Initially, Matis had only SYSADMIN for Sideflix; Jérémy had to create roles/monitor. The earlier DAG used SYSADMIN, never ACCOUNTADMIN, but SYSADMIN was broader than needed. Prepared `governance/10_admin_setup.sql` and `10_verify_access.sql`, runtime SNOWFLAKE_ROLE support in the RSA helper/Core profile/DAG, and removed unnecessary schema creation from the dbt hook because LAB already existed. Syntax checks alone were not treated as least-privilege execution; the actual results are below.

Verified protections: no tracked `.env`, private key or Terraform state; `.gitignore`/`.dockerignore` exclusions; read-only key mount; webhook passed at runtime rather than built into images. State protection follows the actual step 4.2 GCS private/versioned/locked evidence; Matis did not revalidate the bucket independently. Simulated viewing is labeled; public-source periods/attribution appear in the manifest and source documentation.

Submission is this private repository, with no separate copy. IMDb/Netflix exports remain versioned from `0577f62` for exact replay; the repository must remain private while those exports remain, including in its history.

### Actual administrative intervention, 4 November, 19:10–19:20 Paris

Jérémy executed `governance/10_admin_setup.sql` unchanged and then `governance/10b_pipeline_user.sql` on his PC as ACCOUNTADMIN through key-pair authentication. No REDGRAVE object or Terraform resource was changed. Full output: `Etape_10_admin_outputs.txt`.

The initial script granted SIDEFLIX_RUNNER only to MATIS_DOUAY. Jérémy's demonstration jobs otherwise used a user with ACCOUNTADMIN membership, which would not prove strict least privilege. `10b_pipeline_user.sql` therefore creates `SIDEFLIX_PIPELINE` (TYPE=SERVICE, default SIDEFLIX_RUNNER, no secondary roles, no password) with a new RSA pair generated using the lab 2 `gen_key.py`. The private key stays outside Git at `C:/Users/jerem/sideflix_keys`, mounted read-only. Registered public-key fingerprint: `SHA256:ypAUUv/nAeoxCH8PpvzT6RXVnr5hlHhxwjStY1dPhNg=`.

### Actual allowed/denied operations

`Etape_10_access_tests.txt`: **11 checks, all conformant**.

| Context | Operation | Expected | Observed |
| --- | --- | --- | --- |
| SIDEFLIX_ANALYST only, `USE SECONDARY ROLES NONE` | SELECT Gold | Allowed | Allowed, three rows |
| Same | SELECT Bronze, SELECT Silver | Denied | Denied: unauthorized schema |
| Same | Zero-row INSERT Gold | Denied | Denied: no INSERT grant |
| SIDEFLIX_PIPELINE, SIDEFLIX_RUNNER, no secondary roles | SELECT Bronze and Gold | Allowed | Allowed |
| Same | USE ROLE ACCOUNTADMIN / SYSADMIN | Denied | Denied: role not granted |
| Same | CREATE SCHEMA, read ACCOUNT_USAGE, read REDGRAVE | Denied | Denied |

After rebuilding both images and setting private `SNOWFLAKE_USER=SIDEFLIX_PIPELINE` and `SNOWFLAKE_ROLE=SIDEFLIX_RUNNER`, normal run `runner_normal_20261101` succeeded on all four tasks in 1 min 29 s. Evidence: `Etape_10_runner_run.txt`. It issued 94 Snowflake queries, all by SIDEFLIX_PIPELINE/SIDEFLIX_RUNNER, none erroneous. Six identical batches, no added rows, freshness/build PASS=33, one publication for 1 November with 13 sessions / 177.4 minutes. The validated DAG run therefore used no administrator role.

## 10.2 — measured configuration and performance

Raw evidence: `Etape_10_Mesures.json`. Initial SHOW WAREHOUSES: SIDEFLIX_WH, X-Small, STANDARD_GEN_2, auto-suspend 60 s, auto-resume=true; no monitor attached at that initial checkpoint. Query acceleration was already true in the observed configuration; it was not enabled in this step and no associated charge is invented.

The Sideflix query filters directly on usage_date=2026-11-01 and sums sessions/minutes by content_id in daily Gold. Query ID `01c830d1-0002-558c-0002-e4f2001372ea`: 248 ms total, 24 ms execution, 3,072 scanned bytes, six rows. TableScan: three of five partitions, 100% of bytes from data cache. USE_CACHED_RESULT=false during measurement, then restored to its initial true value. Disabled result cache does not imply cold data cache. No arbitrary speedup, clustering or decorative optimization is claimed.

Reading PARTITIONS_SCANNED directly from QUERY_HISTORY_BY_SESSION failed with invalid identifier because that field was not exposed there. The measurement was corrected using GET_QUERY_OPERATOR_STATS, following Demo Content. These are actual Sideflix measurements, not demo values.

### Historical estimate and access limitation

Matis's SYSADMIN could not read ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY or TABLE_STORAGE_METRICS. The WAREHOUSE_METERING_HISTORY table function returned zero rows, which was not interpreted as zero credits. Actual values were subsequently obtained by Jérémy below.

Initial explicit compute estimate: one daily run, 120 s active warehouse per run (approximately one-minute execution plus 60 s auto-suspend), one X-Small Gen2 AWS cluster, 30 days. At 1.35 credits/hour: 30 × 120/3600 × 1.35 = **1.35 credits/30 days**. Ten runs/day would yield 13.5 credits. This was a projection, not a bill or exact billed-duration measurement; extra wakeups, open sessions and cloud services can add cost.

Official source consulted on 4 November 2026: Snowflake Service Consumption Table, table 1(b), effective 4 November 2026: https://www.snowflake.com/legal-files/CreditConsumptionTable.pdf . No currency conversion is made without the account's actual price. Trial credits do not mean zero cost.

Private Git snapshots totaled 8.51 MB excluding caches; Snowflake billable storage was measured separately below. GCS stores Terraform state only, replacing the abandoned S3 roadmap option. Actual GCS cost was unavailable on Matis's workstation and must be checked on Jérémy's Google account. Docker/PostgreSQL/Airflow are local.

### Actual consumption, revised projection and monitor

Observed SIDEFLIX_WH consumption from ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY: 0.164 credits on 3 November and 1.277 credits on 4 November within the recorded reporting window, totaling **1.44 credits** (compute + cloud services). Reporting latency can be several hours. These are chiefly repeated development/incident runs, not the target daily cadence. The raw administrative output is authoritative for the exact query window; the earlier narrative mixed UTC and Paris times.

TABLE_STORAGE_METRICS for SIDEFLIX: 0.48 MB active, 25.1 MB time travel from Bronze COPY/MERGE rewrites, 3.5 KB fail-safe. These are small volumes billed per TB/month; no monetary amount is invented.

Revised 30-day projection from the actual runner run: active queries 18:13:54–18:15:05 UTC (71 s), plus 60 s auto-suspend ≈131 s warehouse/run. 30 × 131/3600 × 1.35 credits/hour ≈ **1.5 credits/month**. Assumptions: one daily run, no other queries, each additional wakeup costs at least 60 s.

Created and attached `SIDEFLIX_MONTHLY`: monthly quota 10 credits, notifications at 50% and 80%, suspension at 100%, WAREHOUSE level. SHOW WAREHOUSES confirms X-Small, 60 s auto-suspend, auto-resume and resource_monitor SIDEFLIX_MONTHLY. The quota allows margin over projected 1.5 credits and observed development consumption. No credits were deliberately consumed to trigger a budget threshold. Monitor emails go to account administrators who opt in through Snowsight; Jérémy enabled them on 4 November at 19:50 Paris.

## 10.3 — stop, resume and later cleanup

`governance/README.md` documents DAG pause, Compose down without deleting volumes, warehouse suspension, then up/check/enable/normal run for the oral defense. Compose/CLI methods were actually used in steps 8/9; a complete shutdown was not triggered during this preparation. Cleanup is targeted and deferred until grading, using the correct IaC state. Nothing was destroyed before the defense.

Before any future Terraform apply, inspect the plan from the GCS backend so the manually attached monitor is not removed. MATIS_DOUAY also has both limited roles, with default secondary roles neutralized, for his own runs. Administrative completion is recorded by commits `ea4d78d` and `b77ff6d`.

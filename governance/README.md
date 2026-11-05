# Step 10 — administrative intervention done: replay procedure, measurements, shutdown/restart and cleanup

*Internal project stage 10 (security, costs and operations); in the root README it belongs to Framework steps 4 and 6 and criterion C7.*

Precondition verified: steps 1–9 completed. **Update of 4 November 2026, 19:20 Paris time (Jérémy): `10_admin_setup.sql` then `10b_pipeline_user.sql` run as ACCOUNTADMIN; roles, monitor and service user SIDEFLIX_PIPELINE created; denials and run under SIDEFLIX_RUNNER verified. Evidence: `evidence/07_security_and_costs/security_costs_report.md`.** The procedure below remains the reference for replaying the intervention.

## Jérémy's exact intervention

1. As ACCOUNTADMIN, read then run `governance/10_admin_setup.sql` (on 4 November Jérémy ran it from his PC with key-pair authentication; Snowsight also works). This script creates SIDEFLIX_ANALYST/SIDEFLIX_RUNNER, grants only the Sideflix objects that are needed, transfers ownership of the Silver/Gold models to the runner so that dbt can replace them (current grants kept), disables default secondary roles for Matis and attaches the monthly monitor. SYSADMIN keeps control through the role hierarchy. No REDGRAVE object or Terraform warehouse is recreated.
2. Keep the outputs of SHOW GRANTS, SHOW RESOURCE MONITORS/WAREHOUSES and of the two credit/storage readings at the end of the script in `evidence/07_security_and_costs/`. In Snowsight, check/configure the monitor notifications for the administrator account with a verified email. The thresholds are visible at 50/80/100%, but no budget alert is claimed as received without evidence; do not artificially consume credits to trigger a threshold. Done on 4 November: the outputs are in [evidence/07_security_and_costs/admin_outputs.txt](../evidence/07_security_and_costs/admin_outputs.txt).
3. `10_verify_access.sql` uses the analyst role only, without secondary roles: Gold SELECT allowed, Bronze SELECT and Gold INSERT denied. The check INSERT writes zero rows even if a grant is wrong. These checks, plus a Silver SELECT and the service-user checks, were run on 4 November at 18:11 UTC during Jérémy's intervention: 11/11 conformant, denials included ([evidence/07_security_and_costs/access_tests.txt](../evidence/07_security_and_costs/access_tests.txt)). To replay them, a user holding SIDEFLIX_ANALYST (for example Matis) runs each statement separately and keeps every result, including the denials.
4. In the private file `airflow/.env`, add `SNOWFLAKE_ROLE=SIDEFLIX_RUNNER` and, on the demo machine, `SNOWFLAKE_USER=SIDEFLIX_PIPELINE` with the folder of its key (`10b_pipeline_user.sql`, key pair generated with the TD 2 lab script `gen_key.py`, which is not part of this repository). Rebuild both images and recreate Airflow to pass the variable through, then launch a normal run dated 1 November and check CURRENT_ROLE/SECONDARY_ROLES, build 33/33 and publication 13 sessions/177.4 min. Done on 4 November with run `runner_normal_20261101`: 94 queries, all as SIDEFLIX_PIPELINE/SIDEFLIX_RUNNER, 0 errors, build 33/33, one publication of 13 sessions/177.4 min ([evidence/07_security_and_costs/runner_run.txt](../evidence/07_security_and_costs/runner_run.txt)). The Python helper, the Core profile and the DAG now accept the variable; the default is SIDEFLIX_RUNNER, so the required grants must exist before a runtime run. LAB is already created in step 4; the dbt hook no longer tries to create a schema.
5. Jérémy then checks the Terraform plan from the real GCS backend before any future apply: the manual attachment of the resource monitor must not be removed by accident. Do not run Terraform from Matis's side, nor apply an unreviewed change.

The analyst role inherits neither from the runner nor from SYSADMIN: SYSADMIN is its parent in the hierarchy and the runner is a sibling, not a child. For another demo user, the administrator will also have to grant the chosen role and neutralize secondary roles; do not share Matis's key. For Rayan, this is prepared in `10c_rayan_analyst.sql`; on 5 November, `SHOW GRANTS OF ROLE SIDEFLIX_ANALYST` listed only MATIS_DOUAY and SYSADMIN, so the script had not been run yet.

## Measurements and costs

See `evidence/07_security_and_costs/step10_measurements.json` and `evidence/07_security_and_costs/security_costs_report.md`. The ACCOUNT_USAGE views are denied to SYSADMIN; the empty result of the metering table function does not prove a zero cost. The credits actually consumed (1.44) and the storage figures were then read from the administrative exports: see `evidence/07_security_and_costs/admin_outputs.txt`. The 10 credits/month budget is a prototype control choice, not an observed invoice.

## Shutdown and restart (10.3)

Snapshots in source/real, code on private GitHub, evidence in `evidence/`, results in Snowflake; run receipts and Airflow database in local airflow/work and airflow/state. Keys and .env stay out of Git.

Once the tasks are finished, in the machine's terminal:

```sh
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags pause sideflix_daily
docker compose -f airflow/docker-compose.yml down
```

Then with SYSADMIN in Snowsight:

```sql
ALTER WAREHOUSE SIDEFLIX_WH SUSPEND;
SHOW WAREHOUSES LIKE 'SIDEFLIX_WH';
```

Do not use `down -v` for the normal shutdown: keep the source database. After suspension, avoid any new query that would wake up the warehouse through auto-resume. An already suspended warehouse does not need a second suspension. This shutdown procedure is documented; it was not part of the recorded runs.

To resume: open Docker Desktop, check the private variables and the authorized role, then:

```sh
docker compose -f airflow/docker-compose.yml up -d --build
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags list-import-errors
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags unpause sideflix_daily
# Wait until the scheduled run for the previous day has failed at check_sources (expected), then:
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags trigger sideflix_daily --run-id oral_normal_20261101 --conf '{"date":"2026-11-01"}'
```

Pick a new run_id for any new execution. Auto-resume wakes up the warehouse on the first authorized query. Checks: four tasks in success, build 33/33, one publication row for 1 November, 13 sessions/177.4 min. Unpausing first starts the scheduled run for the previous day, which has no simulated sessions: it fails at `check_sources` by design, publishes nothing and sends one Slack alert. With `max_active_runs=1`, the 1 November run starts only after that run has failed; no data is invented.

Cleanup only after grading and backup: targeted SIDEFLIX objects, never REDGRAVE; Terraform resources from the real GCS state after reviewing the destroy plan. Destroy nothing before the oral presentation. State bucket/versioning handled separately after the resources are deleted and the necessary evidence is kept; key/trial account under Jérémy's control.

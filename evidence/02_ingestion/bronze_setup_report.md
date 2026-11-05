# Step 4.3 V2 — executed and verified in Snowflake

Group account `tozpkte/ml45551`; session `MATIS_DOUAY`, role `SYSADMIN`, warehouse `SIDEFLIX_WH`. SQL adapted from the labs: `ingestion/04_bronze_v2_setup.sql`. No DROP or replacement of prototype data.

Created or extended `IMDB_RAW`, `MOVIELENS_RAW`, `NETFLIX_RAW`, `WIKIDATA_RAW`, `WIKIMEDIA_RAW` with raw VARIANT, file, timestamp, batch and source metadata. `CATALOG` gained IMDb identity/provenance; `SESSIONS_RAW` gained source/batch metadata. Prepared `PUBLIC_SOURCES_STAGE`, CSV/TSV formats and the `PUBLIC_SOURCE_RUNS` journal. Catalog/session/Gold reference copies were retained in LAB.

Script replay was verified without redefining added-column defaults and with reference copies preserved. Executed `ingestion/04b_check_bronze_v2_setup.sql`; export: `evidence/02_ingestion/bronze_setup_checks.csv`. All seven checks passed:

| Check | Observed | Expected |
| --- | --- | --- |
| Tables for five authentic sources | 5 | 5 |
| Raw/metadata columns | 25 | 25 |
| Catalog metadata | 5 | 5 |
| Session metadata | 5 | 5 |
| Preserved reference catalog | 6 | 6 |
| Preserved raw reference sessions | 32 | 32 |
| Reference minutes on 30 October | 55 | 55 |

The three reference checks (6 catalogue rows, 32 raw sessions, 55 minutes on 30 October) concerned prototype copies kept in `LAB`. They were later removed from `04b_check_bronze_v2_setup.sql`, because those copies do not exist on a clean account; the four structural checks remain.

These checks cover object creation only; the loads and the dbt validation are recorded in [ingestion_report.md](ingestion_report.md) and [dbt_report.md](../04_dbt_and_quality/dbt_report.md).

## Terraform state

The existing Terraform warehouse was kept and no apply was ever run from an empty state. Jérémy then migrated the state to a private, versioned, locked GCS backend, followed by a no-change plan (exit 0): see [terraform_report.md](../03_cloud_and_iac/terraform_report.md).

# Step 4.3 V2 — executed and verified in Snowflake

Group account `tozpkte/ml45551`; session `MATIS_DOUAY`, role `SYSADMIN`, warehouse `SIDEFLIX_WH`. SQL adapted from the labs: `ingestion/04_bronze_v2_setup.sql`. No DROP or replacement of prototype data.

Created or extended `IMDB_RAW`, `MOVIELENS_RAW`, `NETFLIX_RAW`, `WIKIDATA_RAW`, `WIKIMEDIA_RAW` with raw VARIANT, file, timestamp, batch and source metadata. `CATALOG` gained IMDb identity/provenance; `SESSIONS_RAW` gained source/batch metadata. Prepared `PUBLIC_SOURCES_STAGE`, CSV/TSV formats and the `PUBLIC_SOURCE_RUNS` journal. Catalog/session/Gold reference copies were retained in LAB.

Script replay was verified without redefining added-column defaults and with reference copies preserved. Executed `ingestion/04b_check_bronze_v2_setup.sql`; export: `rendu/Etape_4_3_V2_Resultats.csv`. All seven checks passed:

| Check | Observed | Expected |
| --- | --- | --- |
| Tables for five authentic sources | 5 | 5 |
| Raw/metadata columns | 25 | 25 |
| Catalog metadata | 5 | 5 |
| Session metadata | 5 | 5 |
| Preserved reference catalog | 6 | 6 |
| Preserved raw reference sessions | 32 | 32 |
| Reference minutes on 30 October | 55 | 55 |

At this historical checkpoint, the five new datasets were not loaded yet. Object creation alone does not prove ingestion or validation of V2 dbt models; see the subsequent step 5–7 reports.

## State migration follow-up

The existing Terraform warehouse was retained. At the initial 4.3 checkpoint, team state still lived on Jérémy's workstation and migration was pending. No apply was run with empty state.

**Update, 4 November 2026 (Jérémy):** action 4.2 was completed: migration to a private, versioned, locked GCS backend, followed by a no-change plan (exit 0). Step 4 is closed. See `rendu/Etape_4_2_V2_Verifications.md`.

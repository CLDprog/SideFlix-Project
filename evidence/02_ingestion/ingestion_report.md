# Step 5 V2 — executed checks, 4 November 2026

Status: completed. Matis's workstation, user `MATIS_DOUAY`, role `SYSADMIN`, warehouse `SIDEFLIX_WH`, context `SIDEFLIX.BRONZE`. Steps 1–4 were checked against the handover and existing evidence. No Terraform command was executed in this step.

## Methods and results

- **5.1 — lab 2B, watermark/MERGE:** `ingestion/incremental_catalog.py` reads the real PostgreSQL catalog. First pass: six updates, no inserts, total six; replay: no extracted rows or changes. IMDb identity, provenance and metadata are retained. The lab's strict `updated_at > MAX(updated_at)` watermark requires reliable modification timestamps and does not handle deletes.
- **5.2 — lab 2B, controlled update:** `ingestion/verify_catalog_replay.py` works exclusively on two LAB copies. Results: six inserts, replay zero, title change one update, restoration one update, final replay zero. Full before/after comparisons show the real PostgreSQL and Snowflake catalogs unchanged. The first check failed because the PostgreSQL test table was not committed; executing DDL outside the surrounding transaction corrected it. Real data was unchanged.
- **5.3 — lab 2A and pack 05:** `ingestion/load_sessions.py` loads files through PUT/stage/COPY and actually calls both APIs through the existing `requests` collector, then uses PARSE_JSON/VARIANT. Responses are saved under `source/real/api_runs/`, initially outside Git and versioned in the private repository from commit `0577f62`. IMDb identity for all six entities and seven days per article are checked. Responses are merged by batch/URL to prevent duplicates.
- **5.4 — reconciliation and replay:** `ingestion/verify_bronze_v2.py`. All original manifest checksums remain unchanged. New API calls have their own batch hashes, distinct from earlier snapshots. Every row has SOURCE_SYSTEM, _BATCH_ID, _source_file and _loaded_at (UTC session), linked to PUBLIC_SOURCE_RUNS. Exact file/response replay adds zero rows across six batches. COPY was actually replayed without FORCE: “0 files processed” for the four file batches. Grain/key uniqueness checks are listed below.

| Source | Loaded grain and verified volume | Method |
| --- | --- | --- |
| IMDb | Six works, six distinct tconst identifiers | PUT/COPY, six authentic rows selected from the source file |
| MovieLens | Six movies + six links + 74 unique userId/movieId ratings = 86 rows | PUT/COPY, authentic subset selected through the mapping |
| Netflix Top 10 | Three unique week/category/title/season rows for Sicario/Get Out | PUT/COPY; only Sicario is confirmed in the mapping, other matches remain unjoined |
| Wikidata | Six responses, six distinct URLs | Live API → VARIANT |
| Wikimedia | Six responses, 42 distinct article/day observations, 26 October–1 November 2026 | Live API → VARIANT |
| **Simulated** Sideflix sessions | 32 rows, 31 distinct session_id values, one negative duration | PUT/COPY; excluded from the five authentic datasets |

Bronze SESSIONS_RAW also retains the prototype's 32 rows. V2 rows are identified by `SOURCE_SYSTEM=sessions_simulated` and their batch; V2 dbt filters this scope before deduplication. Other archives remain in LAB. The journal also records successful zero-row replays, so its execution count is not fixed.

## Reproduction

From the repository root, with local Snowflake/RSA and PG* variables configured:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r ingestion/requirements.txt
.venv/bin/python ingestion/check_connection.py
.venv/bin/python ingestion/incremental_catalog.py
.venv/bin/python ingestion/verify_catalog_replay.py
.venv/bin/python ingestion/load_sessions.py --public --api-mode live --receipt airflow/work/ingestion_check.json
.venv/bin/python ingestion/load_sessions.py --public --replay-receipt evidence/02_ingestion/ingestion_v2_initial.json --receipt airflow/work/ingestion_replay_check.json
.venv/bin/python ingestion/verify_bronze_v2.py
```

The two receipts in this folder were produced by these commands with `--receipt` pointing here; re-runs write to the Git-ignored `airflow/work/` folder so that the evidence stays unchanged.

Exact replay uses the `api_runs` responses versioned from commit `0577f62` (see `source/README.md`). If unavailable, perform a live collection and create a new receipt rather than claiming to reproduce the previous snapshot. New snapshots may differ and must be documented. No secrets are versioned. Connector 4.8.0 and cryptography 46.0.5 match the pack. Platform detection is disabled before import (`ingestion/check_connection.py`); instance-metadata access is unnecessary.

## Raw evidence

- `python_5_v2_catalog_initial.txt`, `python_5_v2_catalog_replay.txt`, `python_5_v2_catalog_lab.txt`
- `python_5_v2_sources_initial.txt`, `python_5_v2_sources_replay.txt`
- `ingestion_v2_initial.json`, `ingestion_v2_replay.json`: batches and expectations, no private data
- `python_5_v2_reconciliation.txt`: all checks passed

The subsequent step 6 report records adaptation and execution of dbt on V2 data. Earlier dbt results are historical.

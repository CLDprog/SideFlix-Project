# Sideflix — Data Engineering & Cloud Infrastructure

Albert School · Group 6: Matis Douay, Jérémy Caillaud, Rayan Faher Bonne. Oral defense: **6 November 2026, 13:00 (Paris time)**.

Sideflix is a fictional independent-film streaming platform. Its daily batch pipeline ranks the titles to feature each week. It ingests a PostgreSQL catalogue, files and public APIs into Snowflake (AWS, Paris region), transforms and tests them with dbt, orchestrates the run with Airflow in Docker, and declares its warehouse in Terraform.

## Deliverables

| Requested deliverable | Where |
| --- | --- |
| Slides of the oral presentation (16 slides plus two appendix slides, English, with speaker notes) | [deliverables/Sideflix_Oral_Defense.pptx](deliverables/Sideflix_Oral_Defense.pptx) · [PDF export](deliverables/Sideflix_Oral_Defense.pdf) |
| Architecture | [Diagram](docs/architecture.png) · [Components, data flows and choices](docs/architecture.md) |
| Git repository with README | This repository: README, reproducible code and [launch procedure](#running-the-pipeline) |
| Video of the working pipeline (to submit, not graded) | [Airflow run recording, 1 min 21 s](deliverables/Sideflix_pipeline.mov) · [completion proof from the same run's logs](evidence/09_video_run/video_run_verification.json) |
| Optional execution evidence: run IDs, dates, versions, results, checks, replay tests, screenshots | [Evidence index](evidence/README.md) |
| dbt documentation and lineage (Session 4.2 checklist) | [dbt documentation site](docs/dbt/README.md) · [lineage image](docs/dbt_lineage.png) |

The repository is private because it contains IMDb and Netflix exports that may not be redistributed. The professor is given read access by the repository owner. No Snowflake account or key is needed to read the code, documentation and evidence.

## How the project follows the Framework

| Framework step | Section | Evidence folder |
| --- | --- | --- |
| 1. Company and use cases | [Step 1](#step-1--company-and-use-case) | Slides 2–3 |
| 2. At least five real sources | [Step 2](#step-2--five-real-data-sources) | [01_sources](evidence/01_sources/) |
| 3. Different ingestion methods, automated flow | [Step 3](#step-3--ingestion-strategy) | [02_ingestion](evidence/02_ingestion/), [04_dbt_and_quality](evidence/04_dbt_and_quality/), [05_orchestration](evidence/05_orchestration/) |
| 4. Cloud and tools, with justification | [Step 4](#step-4--cloud-and-tools) | [03_cloud_and_iac](evidence/03_cloud_and_iac/), [07_security_and_costs](evidence/07_security_and_costs/) |
| 5. Slides: business context and full architecture | [Step 5](#step-5--architecture-slides-and-business-output) | [08_gold_report](evidence/08_gold_report/) |
| 6. Two real incidents, live run, governance, lineage and documentation | [Step 6](#step-6--resilience-governance-and-live-demonstration) | [06_incidents](evidence/06_incidents/), [07_security_and_costs](evidence/07_security_and_costs/), [09_video_run](evidence/09_video_run/), [10_final_check](evidence/10_final_check/) |

The [evidence index](evidence/README.md) also maps every grading criterion C1–C8 to these files.

## Step 1 — Company and use case

Sideflix is a **fictional** company. Its real-world reference is Netflix, whose public weekly Top 10 is one of the five sources. All figures below are explicit scenario assumptions.

| Item | Scenario |
| --- | --- |
| Revenue model and customers | Subscriptions: 10,000 film-fan subscribers × €7.99 per month ≈ €80k per month (€0.96m per year), ad-free niche catalogue |
| Size, operations, stakeholders | 100 titles, 6 employees, featured titles reviewed every week; subscribers, catalogue manager, independent producers, management |
| Problem and constraints | 100 titles compete for weekly featuring; seven-day figures must be ready by 07:00 Paris time every day; Snowflake budget capped at 10 credits per month (about 1.5 projected) |
| Possible exit | A sale to Netflix: a scenario, not an agreement and not a second use case |

**Use case (one decision, one user).** The **catalogue manager** decides **which titles to feature this week**.

- **Cadence:** computed every day at 06:00 Paris time, figures ready before 07:00, so the seven-day window is current when the weekly decision is taken.
- **Grain:** title × UTC day of session start.
- **Metrics:** valid sessions = distinct `session_id` after exclusions; minutes watched = sum of watched seconds / 60; seven-day ranking by minutes, then sessions.
- **Exclusions:** rows with a missing identifier, an unknown title, an invalid start time or a duration that is not positive or exceeds the runtime are quarantined with their reason; duplicates are removed. An unexpected device value fails a dbt `accepted_values` test, which blocks Gold and the publication.
- **External context:** MovieLens ratings, Wikipedia page views and Netflix Top 10 ranks are shown next to the ranking. They never enter the minutes or the rank.
- **Acceptance test:** 1 November 2026 must give 13 valid sessions and 177.4 minutes, matching an independent calculation from the input files (`source/v2/expected_daily_usage.csv`).

## Step 2 — Five real data sources

Five **authentic** datasets. Each one has its URL, SHA-256 checksum, period, grain and terms of use in [`source/sources_manifest.csv`](source/sources_manifest.csv), detailed in [docs/sources_and_catalogue.md](docs/sources_and_catalogue.md).

| Dataset | Use | Period | Ingestion |
| --- | --- | --- | --- |
| IMDb | Title, type, year and runtime of the six films | Snapshot of 4 Nov 2026 | File, stage + COPY |
| MovieLens | 74 ratings: average and count per film | 1996–2018 | File, stage + COPY |
| Netflix Top 10 | Weekly global ranks; one confirmed match (Sicario, rank 5, week of 9 Mar 2025) | Weekly lists, 4 Jul 2021–1 Nov 2026 | File, stage + COPY |
| Wikidata | Identity (QID), IMDb and Wikipedia links | Response of 4 Nov 2026 | API, requests → VARIANT |
| Wikimedia | Daily Wikipedia page views (42 observations) | 26 Oct–1 Nov 2026 | API, requests → VARIANT |

The six films (Whiplash, Moonlight, Frances Ha, Room, Sicario, Get Out) are matched across sources by IMDb `tconst` and Wikidata QID, not by title. Netflix Top 10 has no identifier, so its single match (Sicario) uses the exact title and was confirmed manually as Netflix title 80046311. The **Sideflix viewing sessions are simulated**: `source/v2/sessions/`, 32 JSON rows over 30 October–1 November 2026. They are not counted among the five real datasets. The raw snapshots in `source/real/` allow an exact replay; downloaded archives and the full IMDb dump are excluded from Git.

## Step 3 — Ingestion strategy

| Source type | Method (course reference) | Landing and controls |
| --- | --- | --- |
| On-premises catalogue: PostgreSQL container | [`ingestion/incremental_catalog.py`](ingestion/incremental_catalog.py): `updated_at` watermark + MERGE (TD 2, part B) | `BRONZE.CATALOG` and `LOAD_RUNS` run log; replay updates nothing |
| Files: IMDb, MovieLens, Netflix and the simulated sessions | [`ingestion/load_sessions.py`](ingestion/load_sessions.py): PUT to an internal stage, then COPY INTO (TD 2, part A) | Raw rows in Bronze with file name, load time, batch ID and source. The batch ID is a hash of the content: a batch already in Bronze is not reloaded, a partial batch stops the run, the COPY aborts on any error and row counts are checked after the load |
| Public APIs: Wikidata and Wikimedia | `requests` with timeout, user agent and saved responses, loaded as VARIANT (resource pack 05) | Raw JSON in Bronze; saved responses allow an exact replay without HTTP calls |

The automated flow is one Airflow DAG, `sideflix_daily`: `ingest_sources` → `check_sources` → `dbt_build` → `publish_daily_usage`. `check_sources` validates batches and completeness per source before any transformation. dbt Silver applies safe typing (`TRY_` functions), quarantine with a reason and deduplication. **Schema validation:** on top of this typing, `not_null`, `unique`, `accepted_values` and `relationships` tests fail the build when a Silver row breaks the expected schema (missing or duplicate key, unexpected category, unknown reference). Each Gold table is built only if the key, category and reference tests on its Silver inputs pass, and publication, a MERGE keyed on the date, runs only after the whole build has passed, including the reconciliation, completeness and Gold tests. Evidence: [ingestion runs and replay](evidence/02_ingestion/ingestion_report.md), [dbt models and tests](evidence/04_dbt_and_quality/dbt_report.md), [Airflow runs](evidence/05_orchestration/orchestration_report.md).

## Step 4 — Cloud and tools

![Sideflix architecture](docs/architecture.png)

| Component | Role | Course method |
| --- | --- | --- |
| PostgreSQL (`source-db` container) | Simulated on-premises catalogue database | Resource pack 04 |
| Snowflake on AWS eu-west-3 (Paris) | Bronze, Silver and Gold storage and compute; X-Small `SIDEFLIX_WH` warehouse, 60 s auto-suspend | TD 2, 3.2, 3.3 |
| dbt (`dbt/sideflix_dbt`) | 9 Silver views, 2 Gold tables, 21 tests, run-results audit hook | TD 3.2, 3.3; packs 03 and 07 |
| Docker + Airflow (`docker/`, `airflow/`) | Containerised jobs (DockerOperator), daily schedule, 2 retries, Slack alert on final failure | TD 4.2; packs 06 and 07 |
| Terraform (`terraform/`) | `SIDEFLIX_WH` declared in code; state in a private, versioned, locked GCS bucket | TD 4.2; pack 09 |
| `governance/` | `SIDEFLIX_RUNNER` pipeline role, read-only `SIDEFLIX_ANALYST`, `SIDEFLIX_PIPELINE` service user, budget monitor | Snowflake roles and grants from the labs |

**Why these choices.** A weekly decision on a small volume only needs a daily batch, so Kafka, CDC, Snowpipe and Iceberg would add operations without value. Snowflake was chosen over BigQuery for SQL plus VARIANT on JSON, the course account and an auto-suspending warehouse. dbt gives versioned, tested transformations, and Airflow gives runs that can be replayed by date. Alternatives and trade-offs: [docs/architecture.md](docs/architecture.md).

**Cloud use and costs.** The pipeline actually traverses Snowflake on AWS. Google Cloud Storage holds **only** the Terraform state: this is disclosed against the checklist wording "1 cloud", and the setup does not claim a single provider. Observed consumption was 1.44 credits during development and tests. The projection is about 1.5 credits per month (30 runs × 131 s of warehouse time × 1.35 credits per hour for the X-Small Gen2 warehouse), not an invoice. A resource monitor caps the warehouse at 10 credits per month, with notifications at 50% and 80% and suspension at 100%. [Measured evidence](evidence/07_security_and_costs/security_costs_report.md).

## Step 5 — Architecture, slides and business output

The [slides](deliverables/Sideflix_Oral_Defense.pptx) present the business context, the five sources, the full architecture, the results, the incidents, the operations and the costs. The [architecture document](docs/architecture.md) details every component and data flow.

![Snowsight chart: minutes watched by film](evidence/08_gold_report/2_minutes_chart.jpg)

*Simulated Sideflix viewing; analysis window 26 October–1 November 2026, with sessions on 30 October–1 November. Screenshot taken in Snowsight under the read-only analyst role; original UI language kept.*

- **Weekly ranking:** Whiplash first (7 sessions, 112.7 minutes), then Moonlight, Sicario, Frances Ha, Room and Get Out.
- **Daily output, 1 November:** 13 valid sessions and 177.4 minutes, one publication row. All three days: 30 valid sessions and 454.2 minutes.
- **Reproducible queries:** [docs/snowsight_gold_report.sql](docs/snowsight_gold_report.sql). Screenshots and values: [Snowsight report](evidence/08_gold_report/snowsight_report.md).

## Step 6 — Resilience, governance and live demonstration

**Two real incidents, actually executed, with recovery** ([incident report](evidence/06_incidents/incident_report.md)). Both were executed on 4 November and rehearsed again with the final code on 5 November, so they can be run live at the oral ([live procedure](docs/live_demo_runbook.md#showcase-the-two-incidents-live-with-recovery)):

1. **Invalid data:** an invalid device injected into an isolated copy of a batch → the dbt `accepted_values` test fails after 3 attempts → Gold and the publication stay unchanged → Slack alert received → only the test batch is removed → the corrective run passes 33/33 with unchanged figures.
2. **Crash after the publication write:** the job crashes right after its MERGE → Airflow retries automatically → attempt 2 succeeds → still one row for the date, same totals, no double counting ([task logs](evidence/06_incidents/incident_9_2_logs/)).

Also checked: a day without data fails the source check, publishes nothing and alerts Slack, and two replays of the same date add no rows. A missing-file procedure is documented. A real upstream change was absorbed on 5 November: Wikidata replaced the English label of Moonlight with its multilingual default label, and the Silver model now falls back to that label.

**Quality.** 11 models + 21 tests + 1 audit hook = **33 successful dbt operations**; source freshness 2/2, measured from the ingestion journal so that replays of a past date stay valid; reconciliation 32 raw rows = 30 valid + 1 quarantined + 1 duplicate; Gold is checked against an independent calculation.

**Governance and security.** The pipeline runs under `SIDEFLIX_RUNNER`. The analyst role reads Gold only: reads of Bronze and Silver and all writes are denied. All 11 allow/deny checks are recorded. RSA keys are mounted read-only at runtime. `.env` files, keys, the webhook and the Terraform state are kept out of Git.

**Lineage and documentation.** The [dbt documentation site](docs/dbt/README.md) was generated from the delivered code. It shows sources, models, columns, tests and the lineage graph from Bronze to Gold.

**Live run at the oral.** The presenters will run `sideflix_daily` for 1 November live, check the publication, run the allowed/denied access checks and open the lineage and documentation: see the [live demonstration runbook](docs/live_demo_runbook.md). The live sequence was rehearsed with the delivered code on 5 November 2026: unpausing the DAG started the scheduled run for 4 November, which failed at `check_sources` by design and published nothing; the final run `final_verification_20261105` then succeeded under `SIDEFLIX_RUNNER` (4 tasks, 95 queries, 0 errors), with source freshness 2/2, `PASS=33` and 13 sessions / 177.4 minutes published once ([rehearsal and final run](evidence/10_final_check/final_check_verification.json)). The video and the saved evidence are fallbacks and do not replace the live run.

## Running the pipeline

Prerequisites: Docker Desktop; a Snowflake account and an RSA key pair for its user; an alert webhook supplied privately. Python 3.11+ is needed for local checks or dbt outside Docker. Terraform 1.9+ and access to the shared GCS state are needed only for infrastructure changes. The evidence index lists the exact recorded versions.

### 1. One-time bootstrap (administrator, separate from runtime)

On the **existing team account**, keep the existing state and objects; do not recreate or replace them. On a new account:

1. Run [`ingestion/00_create_sideflix_objects.sql`](ingestion/00_create_sideflix_objects.sql) as SYSADMIN.
2. Configure Terraform with [`terraform/README.md`](terraform/README.md). On a new account, first point `terraform/backend.tf` to your own private bucket (or remove it to keep a local state): the delivered backend is the team's shared state. Review the plan and apply only an intended new warehouse. For the team's existing warehouse, use the real shared state; never apply from an empty state.
3. Run [`ingestion/01_bronze_setup.sql`](ingestion/01_bronze_setup.sql), then [`ingestion/04_bronze_v2_setup.sql`](ingestion/04_bronze_v2_setup.sql) as SYSADMIN. They create Bronze plus the publication and audit tables that the later grants need.
4. As ACCOUNTADMIN, follow [`governance/README.md`](governance/README.md): roles and monitor in `10_admin_setup.sql`, then the service user in `10b_pipeline_user.sql`. On a new account, replace the team user `MATIS_DOUAY` in `10_admin_setup.sql` with your own user, or remove those lines if only `SIDEFLIX_PIPELINE` runs the pipeline. Register its public RSA key privately. Administrative roles are never pipeline runtime roles.

### 2. Private runtime configuration

Create the Git-ignored runtime folders with `mkdir -p airflow/work airflow/state` (the job containers bind-mount `airflow/work`), then copy `airflow/.env.example` to `airflow/.env`. Fill in the Snowflake account and user, the absolute paths of the repository, `airflow/work` and the key folder, the webhook and the host UID/GID. The runtime role is **SIDEFLIX_RUNNER**. The service user is `SIDEFLIX_PIPELINE`; each member may instead use their own authorized user and key. Never copy someone else's private key or commit `.env`.

### 3. Build, start and run (from the repository root)

```sh
docker build -f docker/ingestion.Dockerfile -t sideflix-ingest:1.0.0 .
docker build -f docker/dbt.Dockerfile -t sideflix-dbt:1.0.0 .
docker compose -f airflow/docker-compose.yml up -d --build
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags list-import-errors
```

Compose creates and seeds the local PostgreSQL catalogue. Keep **only one active Airflow scheduler** for the group against the shared account. Open [Airflow](http://localhost:8080) and unpause `sideflix_daily`. Airflow then immediately starts the latest scheduled run, which targets the previous day: it has no simulated sessions, so it fails at `check_sources` by design, publishes nothing and sends one Slack alert. Once it has failed, trigger the demonstration run with:

```json
{"date":"2026-11-01"}
```

Or from the command line, with a new run ID each time:

```sh
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags trigger sideflix_daily --conf '{"date":"2026-11-01"}'
```

All four tasks must succeed: `ingest_sources` → `check_sources` → `dbt_build` → `publish_daily_usage`. The simulated input covers **30 October–1 November 2026**; any other day fails its completeness check and publishes nothing.

### 4. Verify the outputs (read-only)

As SIDEFLIX_RUNNER with secondary roles disabled:

```sql
USE ROLE SIDEFLIX_RUNNER;
USE SECONDARY ROLES NONE;
USE WAREHOUSE SIDEFLIX_WH;
SELECT usage_date, SUM(valid_sessions) AS sessions, SUM(minutes_watched) AS minutes
FROM SIDEFLIX.GOLD.GOLD_CONTENT_DAILY
WHERE usage_date = '2026-11-01' GROUP BY 1; -- 13 sessions, 177.4 minutes
SELECT * FROM SIDEFLIX.LAB.DAILY_USAGE ORDER BY usage_date; -- one row per date
SELECT * FROM SIDEFLIX.GOLD.GOLD_EDITORIAL_WEEKLY ORDER BY editorial_rank;
```

Analyst queries: [`docs/snowsight_gold_report.sql`](docs/snowsight_gold_report.sql). Allowed/denied checks: [`governance/10_verify_access.sql`](governance/10_verify_access.sql). Stop, resume and clean-up procedure: [`governance/README.md`](governance/README.md); do not destroy the infrastructure before grading.

## Repository structure

| Folder | Content |
| --- | --- |
| `deliverables/` | Slides and pipeline video |
| `docs/` | Architecture, sources and catalogue, dbt documentation, live demonstration runbook, Snowsight queries |
| `source/` | Catalogue, five authentic snapshots and their manifest, simulated sessions, independent expected result |
| `ingestion/` | Snowflake setup SQL, Python ingestion, publication and verification scripts |
| `dbt/` | Bronze source declarations, Silver and Gold models, tests, profiles, pinned versions |
| `docker/`, `airflow/` | Job images, Compose stack and the `sideflix_daily` DAG |
| `terraform/` | Warehouse as code and remote GCS state configuration |
| `governance/` | Roles, service user, access checks, budget monitor and operating procedure |
| `evidence/` | Execution evidence by pipeline stage, indexed in [evidence/README.md](evidence/README.md) |

## Scope, limitations and contributions

- **Company:** the grading matrix asks for a convincing fictional company, while Framework step 1 mentions a real-world enterprise. Sideflix is explicitly fictional and grounded in Netflix as the real reference; no real acquisition is claimed.
- **Data:** Sideflix sessions are simulated and labelled as such. The external datasets cover different historical periods, and only Sicario has a confirmed Netflix Top 10 match.
- **Cloud:** data and compute run on Snowflake (AWS Paris); GCS stores the Terraform state only.
- **Shared account:** the Snowflake trial account also holds `REDGRAVE`, the course's lab database. Sideflix never modifies it, and the [recorded access tests](evidence/07_security_and_costs/access_tests.txt) show that `SIDEFLIX_RUNNER` cannot read it.
- **Evidence:** the raw logs, receipts and screenshots keep their captured values (only human-written notes in some text logs were translated). Some show French labels from the team's scripts or the Snowsight interface; the [evidence index](evidence/README.md) explains them.

**Contributions** (each member explains their own part at the oral):

- **Matis Douay:** collection of the five sources and manifest, v2 ingestion, dbt Silver/Gold and tests, the two incidents, the video, and the executed Snowsight captures.
- **Jérémy Caillaud:** Snowflake account and foundation, Terraform and shared GCS state, Docker/Airflow runs and Slack alerting, limited roles, costs and budget, slides.
- **Rayan Faher Bonne:** owner of the Gold consumption layer (Snowsight reporting under the read-only analyst role), presented at the oral. The saved captures were executed by Matis; the repository does not claim Rayan executed them.

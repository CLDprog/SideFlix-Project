# Sideflix — Data Engineering & Cloud Infrastructure

Albert School · Group 6: Matis Douay, Jérémy Caillaud, Rayan Faher Bonne. Oral defense: **6 November 2026, 13:00 Europe/Paris**.

## Submission files

| Required deliverable | Open here |
| --- | --- |
| Presentation — 21 slides, English | [Sideflix Oral Defense](deliverables/Sideflix_Oral_Defense.pptx) |
| Architecture | [Full diagram](docs/architecture_v2.png) · [Choices and data flows](docs/architecture_v2.md) |
| Git repository with README and reproducible code | This repository; setup below |
| Pipeline video — mandatory, not graded | [Original Airflow recording, 1 min 21 s](deliverables/Sideflix_pipeline.mov) · [Final-task completion evidence](rendu/video_run_verification.json) |
| Optional execution evidence | [Evidence index: requirements, runs, versions](rendu/INDEX_PREUVES.md) |
| Gold results | [Snowsight table and chart](rendu/Restitution_Snowsight.md) · [SQL](docs/snowsight_rayan.sql) |
| dbt documentation and lineage | [Documentation](docs/dbt/README.md) · [Lineage image](docs/dbt_lineage.png) |

The video shows the actual Airflow execution. Its last frame still shows publication running; the unmodified logs of that same run prove successful completion. The video and saved evidence **do not replace the live oral demonstration**. [Live demonstration checklist](docs/conducteur_oral.md).

This repository is private. Its owner must grant the teacher access before submission. No Snowflake login or private key is needed to read the submitted evidence. [Final audit and remaining human actions](docs/DELIVERY_AUDIT.md).

## The business need

Sideflix is a **fictional** streaming platform, inspired by the real Netflix and specialized in independent cinema (assumptions: 10,000 subscribers at €7.99 per month, 100 content items, 6 employees; a sale to Netflix is the exit envisaged in the scenario).

- **User**: the catalog manager.
- **Decision**: which content to feature this week.
- **Cadence**: computed every day at 06:00 (Paris time), figures available before 07:00.
- **Grain**: content × UTC day of session start.
- **Metrics**: distinct valid sessions and minutes watched (sum of seconds / 60), seven-day ranking, with the real context from external sources displayed alongside and never mixed into the rank.

## Architecture as executed

![Sideflix architecture](docs/architecture_v2.png)

| Component | Role | Course method |
| --- | --- | --- |
| PostgreSQL (`source-db`, container) | "On-premises" catalog database | Pack 04 |
| `ingestion/incremental_catalog.py` | Catalog to Bronze via watermark + MERGE | TD 2, part B |
| `ingestion/load_sessions.py` | Files and sessions via PUT, stage, COPY INTO; API via requests into VARIANT | TD 2, part A; pack 05 |
| Snowflake (AWS eu-west-3) | Bronze, Silver, Gold; X-Small SIDEFLIX_WH warehouse | TD 2, 3.2, 3.3 |
| dbt (`dbt/sideflix_dbt`) | 9 Silver views (quarantine, deduplication), 2 Gold tables, 21 tests | TD 3.2, 3.3; packs 03 and 07 |
| Docker + Airflow (`docker/`, `airflow/`) | `sideflix_daily` DAG: ingest, check, dbt build, publish; Slack alert | TD 4.2; packs 06 and 07 |
| Terraform (`terraform/`) | SIDEFLIX_WH warehouse; state in a private, versioned, locked GCS bucket | TD 4.2; pack 09 |
| `governance/` | SIDEFLIX_ANALYST and SIDEFLIX_RUNNER roles, service user, budget monitor | TD 2 |

Details: [docs/architecture_v2.md](docs/architecture_v2.md).

## The data

Five **authentic** datasets, each with URL, SHA-256 checksum, period, grain and terms of use in [`source/sources_manifest.csv`](source/sources_manifest.csv); details in [docs/sources_and_catalogue.md](docs/sources_and_catalogue.md).

| Dataset | Use | Period |
| --- | --- | --- |
| IMDb | Title, type, year, runtime of the six works | Snapshot of 4 Nov 2026 |
| MovieLens | 74 ratings: average and count per work | 1996 to 2018 |
| Netflix Top 10 | Weekly ranks; one confirmed match (Sicario) | Week of 9 Mar 2025 |
| Wikidata | Identity (QID), IMDb and Wikipedia links | Response of 4 Nov 2026 |
| Wikimedia | Wikipedia page views per day (42 observations) | 26 Oct to 1 Nov 2026 |

The **Sideflix sessions are simulated** (`source/v2/sessions/`, 32 rows over three days) and do not count among the five datasets. The expected result, computed independently, is in `source/v2/expected_daily_usage.csv`. The raw snapshots (`source/real/`) allow an exact replay. They stay in this private repository (group members, plus read-only access for the professor's grading): the IMDb and Netflix terms do not allow their redistribution, so the repository is not made public as long as these exports are in it, history included.

## Running the pipeline

Prerequisites: Docker Desktop; a Snowflake account and an RSA key belonging to its user; an alert webhook supplied privately. Python 3.11+ is needed for local verification/dbt. Terraform 1.9+ and access to the existing GCS state are needed only for infrastructure operations. Use the recorded versions in the evidence index for exact reproduction.

### 1. Bootstrap once — administrator, separate from runtime

On an **existing team account**, retain the existing state and objects; do not recreate or replace them. On a new account:

1. Run [`ingestion/00_create_sideflix_objects.sql`](ingestion/00_create_sideflix_objects.sql) as SYSADMIN.
2. Configure Terraform using [`terraform/README.md`](terraform/README.md). Review its plan and apply only an intended new warehouse. For the team's existing warehouse, use its real shared state; never apply from an empty state.
3. Run [`ingestion/01_bronze_setup.sql`](ingestion/01_bronze_setup.sql), then [`ingestion/04_bronze_v2_setup.sql`](ingestion/04_bronze_v2_setup.sql) as SYSADMIN. These create Bronze and the publication/audit tables required by subsequent grants.
4. As ACCOUNTADMIN, follow [`governance/README.md`](governance/README.md): roles/monitor in `10_admin_setup.sql`, then the service user in `10b_pipeline_user.sql`. Associate its public RSA key privately. Administrative roles are not pipeline runtime roles.

### 2. Private runtime configuration

Copy `airflow/.env.example` to `airflow/.env`. Fill in the Snowflake account/user, absolute repository/work/key-directory paths, webhook and host UID/GID. The runtime role is **SIDEFLIX_RUNNER**. The dedicated service user is `SIDEFLIX_PIPELINE`; each member may instead use their own authorized user and own key. Never copy someone else's private key or commit `.env`.

### 3. Build and start — repository root

```sh
docker build -f docker/ingestion.Dockerfile -t sideflix-ingest:1.0.0 .
docker build -f docker/dbt.Dockerfile -t sideflix-dbt:1.0.0 .
docker compose -f airflow/docker-compose.yml up -d --build
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags list-import-errors
```

Compose creates/seeds the local PostgreSQL catalogue. Use only **one active group Airflow scheduler** against the shared account. Open [Airflow](http://localhost:8080), enable `sideflix_daily`, and trigger with:

```json
{"date":"2026-11-01"}
```

Or, with a new run ID each time:

```sh
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags trigger sideflix_daily --conf '{"date":"2026-11-01"}'
```

Four tasks must succeed: `ingest_sources` → `check_sources` → `dbt_build` → `publish_daily_usage`. The three-day simulated input covers **30 October–1 November 2026**. A run for a different day deliberately fails its completeness check and publishes nothing; the live demo must use the explicit date above.

### 4. Verify the outputs — read-only

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

Analyst read-only results: [`docs/snowsight_rayan.sql`](docs/snowsight_rayan.sql). Allowed/denied policy checks: [`governance/10_verify_access.sql`](governance/10_verify_access.sql). Stop/resume: [`governance/README.md`](governance/README.md); do not destroy infrastructure before grading.

## Results, resilience and governance

- **Daily result, 1 November:** 13 valid sessions / 177.4 minutes; one publication row. Across all three days: 30 valid sessions / 454.2 minutes.
- **Weekly decision:** Whiplash ranks first, with 7 sessions / 112.7 minutes. External ratings, page views and Netflix ranks provide dated context and never enter the minutes calculation.
- **Quality:** 11 models + 21 tests + 1 audit hook = **33 successful dbt operations**; source freshness 2/2. Reconciliation: 32 raw rows = 30 valid + 1 quarantined + 1 duplicate.
- **Incident 1, actually executed:** invalid device on an isolated test batch → accepted-values failure → Gold/publication blocked → Slack alert → targeted batch removal → successful rebuild and publication. [Failure and recovery](rendu/Etape_9_V2_Verifications.md).
- **Incident 2, actually executed:** deliberate crash after publication MERGE → Airflow retry → same single row and same values, without double counting. [Retry logs](rendu/incident_9_2_logs/).
- **Security:** dedicated pipeline user/limited role, analyst Gold read-only, RSA keys injected at runtime; positive and negative access checks are recorded. Airflow's local root/socket exception follows the lab; job containers run non-root.
- **Costs:** 1.44 credits observed during development/testing; about 1.5 credits/month projected, not an invoice. Monitor: 10 credits/month, notifications at 50/80%, suspend at 100%; warehouse auto-suspend 60 s. [Measured evidence](rendu/Etape_10_V2_Verifications.md).

![Snowsight minutes watched by film](rendu/restitution_snowsight/2_graphique_minutes.jpg)

*Simulated Sideflix viewing; analysis window 26 October–1 November 2026, with sessions available on 30 October–1 November. Original Snowsight screenshots and execution logs are preserved as captured, including their original UI language.*

## Course alignment and repository structure

The project follows the Framework's six steps: company/use case → sources → ingestion → cloud/tools → architecture/slides → incidents, governance and live demonstration. The [evidence index](rendu/INDEX_PREUVES.md) maps each step and C1–C8 to actual files.

| Folder | Purpose |
| --- | --- |
| `deliverables/` | Presentation and original pipeline video |
| `source/` | Final catalogue, five authentic snapshots, manifest, simulated sessions and independent expected result |
| `ingestion/` | Setup SQL, course-based Python ingestion, publication and verification |
| `dbt/` | Bronze declarations, Silver/Gold models, tests, profiles and pinned dependencies |
| `docker/`, `airflow/` | Job images and the single scheduled DAG |
| `terraform/`, `governance/` | Infrastructure, least-privilege policies, budget and operating procedures |
| `docs/` | Architecture, sources, dbt documentation and oral/video procedures |
| `rendu/` | Final execution evidence, incident/recovery logs and Snowsight captures |

Methods: watermark/MERGE (TD 2B), PUT/stage/COPY (TD 2A), requests/VARIANT (pack 05), dbt Bronze/Silver/Gold and tests (TD 3.2/3.3), DockerOperator/retries/alerting (TD 4.2, packs 06–07), warehouse and remote Terraform state (TD 4.2, pack 09). No additional Kafka, CDC, Iceberg or application is required for this batch use case.

## Scope, limitations and contributions

The grading matrix C1 requests a convincing fictional company; the Framework asks for a real-world enterprise. **Sideflix is explicitly fictional, grounded in Netflix as the real industry reference**. A hypothetical sale to Netflix is not an existing agreement.

Data/compute use Snowflake on **AWS Paris**; **GCS stores Terraform state only**. This is disclosed against the checklist wording “1 cloud”; the setup does not claim a single provider. Sessions are simulated, external datasets have different historical periods, and only Sicario has a confirmed Netflix Top 10 match. The monitor's email delivery and teacher's private-repository invitation require their account owners to verify them.

Contributions: **Matis** — sources, v2 ingestion/dbt/tests, incidents, video and executed Snowsight captures; **Jérémy** — Snowflake/Terraform, Docker/Airflow, alerting, administration, governance/cost validation and deliverables; **Rayan** — assigned ownership and oral presentation of the Gold consumption layer. The saved captures were executed by Matis; the repository does not claim Rayan executed them. Each member must explain their actual pipeline contribution at the oral.

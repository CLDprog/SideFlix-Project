# Pipeline video: Airflow recording

The submitted video was recorded on Matis's Mac on 4 November 2026. It is the **1 minute 21 second, silent, Airflow-only** recording of the run processing 1 November. The README links the versioned `.mov` file. Ingestion, source checks and dbt build succeed in the recording; **publication is still running at its end**. Do not describe the video as showing all four completed tasks. Completed-run and publication evidence is provided separately in `rendu/INDEX_PREUVES.md`.

The video is a requested deliverable even though the course identifies it as ungraded. It does not replace the Framework's live pipeline run during the presentation. Snowsight results, incident recoveries and lineage are documented separately.

## If a replacement Airflow-only recording is needed

1. Confirm that only one Airflow scheduler is active. Build both images and start Compose with the README commands. Use `SNOWFLAKE_ROLE=SIDEFLIX_RUNNER` in the private configuration and check that the DAG has no import errors.
2. Open Airflow at `http://localhost:8080`, select `sideflix_daily`, and prepare its Runs page. Close private files and notifications. Never display `.env`, keys, passwords or webhook URLs.
3. On Mac, press **Shift + Cmd + 5**, select the Airflow area, and start recording.
4. Trigger a new run with a fresh ID and `{"date":"2026-11-01"}`. Do not use an incident parameter. Keep this new run selected.
5. Wait for all four tasks to succeed. Show their logs: ingestion batches, `SOURCE_CHECKS_PASS`, build `PASS=33` / `ERROR=0`, then publication **13 sessions / 177.4 minutes** and `PUBLICATION_UNIQUE_DATE_PASS`.
6. Return to the completed run, stop recording, and verify playback and absence of secrets. Save with a clear filename and update the README link if replacing the submitted recording.

Do not describe an unfinished or failed run as a completed execution. The chosen simulated input dates end on 1 November; an unsupported date fails the source check intentionally. To stop the local stack after use, pause the DAG, then run `docker compose -f airflow/docker-compose.yml down` without `-v`.

## Completion evidence for the recorded run

The original recording is preserved unchanged in `deliverables/Sideflix_pipeline.mov`. Its manual run `manual__2026-11-04T19:47:52.946628+00:00` completed at 19:48:59 UTC. `rendu/video_run_verification.json` and `rendu/video_run_logs/` preserve its actual 33/33 build, MERGE of 13 sessions / 177.4 minutes and publication uniqueness marker. These logs support completion beyond the last recorded frame; they are not an additional screen recording.

# 9.3 — missing-file recovery procedure (not an executed simulation)

1. Identify the failing source/file and requested batch/date in Airflow logs. Look up the expected path and SHA-256 in `source/sources_manifest.csv`. Do not replace missing data with zeros.
2. The collector reuses existing files and can download some missing files again. If retrieval fails or a required file remains absent, `ingest_sources` fails; an incomplete received batch fails `check_sources`. In either case, dependencies block build/publication and the callback notifies after retries.
3. Restore only the affected snapshot from the private repository, preserving unrelated work. After confirming the file is missing, for example:

```sh
git restore --source=HEAD -- source/real/netflix/all-weeks-global.tsv
```

4. Run `shasum -a 256 source/real/netflix/all-weeks-global.tsv` and compare against the manifest. Do not silently accept a snapshot with a different period/checksum. Exact replay responses can likewise be restored from their tracked `source/real/api_runs/` path.
5. Rerun the same day with a new run_id and no incident option. For the 1 November demonstration:

```sh
docker compose -f airflow/docker-compose.yml exec airflow /entrypoint airflow dags trigger sideflix_daily --run-id file_recovery_20261101 --conf '{"date":"2026-11-01"}'
```

6. Verify all four tasks succeed, batches/volumes match expectations and publication is unique (13 sessions / 177.4 minutes for this date). Retain logs/check results in `evidence/06_incidents/` and record the recovery in the team notes.

A physically missing file is first handled by the collector, so failure may occur during ingestion rather than always in `check_sources`. Both paths block publication. This documented procedure is not a third actually tested incident and does not replace 9.1/9.2 evidence.

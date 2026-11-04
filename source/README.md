# Public sources and simulation

Run `python source/collect_public_data.py` from the repository root, with `source/requirements.txt` installed. The collector does not write to any database and does not modify the historical fictitious events. It downloads MovieLens/Netflix if missing, identifies the six Wikidata works by their IMDb P345, retrieves seven days of user pageviews, then filters six records from the gzipped IMDb feed. Responses that are already present are reused.

The 19 manifest files and the 12 responses in `source/real/api_runs/` are versioned in this private GitHub repository, shared with the three group members and, once its owner has invited her, with the professor (read-only, for grading); they are not published. Downloaded archives, full IMDb dumps and generated landing files stay excluded from Git. A `git -c core.autocrlf=false pull --ff-only` retrieves the exact snapshots without a new collection or any line-ending conversion (notably on Windows). The original line endings of the sources are preserved so that the SHA-256 hashes still match. The manifest describes files, URLs, SHA256 and time of the check; the initial download date of the MovieLens files provided by Matis is unknown. A check is not a new extraction. The pageview period runs from October 26 to November 1, 2026; the MovieLens ratings and Netflix rankings are historical. Details in the collection report.

Terms, attributions, grains/periods and curation are documented in `docs/sources_and_catalogue.md` and the manifest. Sharing is limited to this private repository: the three members and, for grading, the professor (read-only). No commercial use and no film distribution rights are claimed. The IMDb (`real/imdb/`) and Netflix (`real/netflix/`) exports are not under a redistribution license: the repository must not be made public while they are in it, Git history included. Wikidata (CC0), the Wikimedia statistics and MovieLens keep their attributions, and the MovieLens license `real/movielens/ml-latest-small/README.txt` stays intact.

`source/v2/sessions/` contains explicitly simulated events; `source/v2/expected_daily_usage.csv` holds their expected results, computed locally. The Bronze v2 load and the replay succeeded (see `rendu/Etape_5_V2_Verifications.md`), and then so did the dbt v2 transformation (see `rendu/Etape_6_V2_Verifications.md`). Historical prototype fixtures were removed from the final delivery; the final simulated input is `source/v2/sessions/`.

## Loading the real catalog (TD 2)

Existing local PostgreSQL database `sideflix`, standard PG* variables (host 127.0.0.1 by default). From the root: `python source/03_load_real_catalog.py`. The script saves the previous catalog only once in `lab.catalog_reference`, adds the IMDb identifier/provenance, then applies an UPSERT. An identical replay does not modify `updated_at`. The obsolete prototype seed scripts numbered 01/02 were removed from the final tree. Evidence: `rendu/Etape_3_2_V2_Verifications.md`. This local load is not a Snowflake ingestion.

## Exact replay on another machine

The original API responses of the manifest remain in `real/wikidata/` and `real/wikimedia/`. The responses actually ingested are kept separately in `real/api_runs/`, by batch_id; they may differ from the initial snapshot. To replay the verified batch, use the already versioned receipt:

```sh
python ingestion/load_sessions.py --public --replay-receipt rendu/ingestion_v2_initial.json --receipt rendu/ingestion_v2_replay.json
```

This command uses the saved responses without calling the APIs again. Private variables and keys remain specific to each machine and outside Git. The SHA-256 hashes in the manifest describe the bytes of the sources; only `usage_attribution` was updated for this sharing in the private repository. Step 8 was then run by Jérémy on his PC (see `rendu/Etape_8_V2_Verifications.md`); his PostgreSQL/Compose adaptations are separate from this data sharing.

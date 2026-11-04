# V2 collection — executed checks

Local collection on 4 November 2026. No publication or PostgreSQL/Snowflake changes were performed in this collection step.

- Five distinct datasets: IMDb, MovieLens, Netflix Top 10, Wikidata and Wikimedia.
- Technical catalog: Whiplash (2014), Moonlight (2016), Frances Ha (2012), Room (2015), Sicario (2015) and Get Out (2017).
- IMDb: six authentic records retained unchanged, each with type `movie` and positive runtime. The script filters the official gzip stream; the full dump is not retained.
- MovieLens: 9,742 movies/links and 100,836 ratings; unique keys, no orphan movie references, ratings from 0.5 to 5 in 0.5 increments and unique user/movie pairs. There are 74 ratings for the six selected movies.
- Wikidata: six entities, verified IMDb P345 mappings, retained QIDs and English article references.
- Wikimedia: six articles × seven days = 42 observations, unique timestamps and nonnegative views. Period: 26 October–1 November 2026, all-access/user. Raw JSON responses retained. An HTTP 429 was retried after a delay without fetching existing snapshots again.
- Netflix: 8,884 rows. Sicario appears in the week of 9 March 2025 at rank 5; the identity of the 2015 movie is corroborated by official Netflix title 80046311. Get Out was not marked as a verified mapping. These historical periods differ from the simulated viewing events.
- All manifest file checksums were checked successfully.
- Isolated final simulation: `source/v2/sessions`, 32 raw rows = 30 valid sessions + one rejection + one duplicate. Daily expectations are in `expected_daily_usage.csv`; viewing provenance is explicitly `sideflix_simulated`. The 30 October reference is A=45 minutes/2 sessions and B=10 minutes/1 session.
- The original prototype was copied unchanged to `source/fixtures/reference`; the original files were also retained in this historical collection step. These obsolete prototype fixtures were subsequently removed from the final delivery tree.

## Reproduction

From the repository root, with `requests` installed as in the course:

```sh
python source/collect_public_data.py
```

The script reuses retained API responses and the IMDb subset. It downloads MovieLens and Netflix if their expected files are missing. Keep the exact snapshots: a later extraction can differ.

## Historical collection follow-up

The initial check still required documenting terms, attribution, period and grain in the manifest, and adding catalog curation references. The six movies are a technical selection, not proof of distribution rights. IMDb redistribution requires checking its terms.

GitHub access was restored after that initial check. The group repository was cloned and additions preserved existing ingestion/Terraform work. Raw snapshots, initially local, were versioned in the private repository from commit `0577f62` for exact replay, without public redistribution; code, mapping, manifest and simulation were shared as well. The published commit was recorded in Notion. These local collection checks do not themselves prove a V2 cloud run. See the later step reports for completed ingestion and processing.

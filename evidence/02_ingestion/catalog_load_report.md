# Step 3.2 V2 — verified in local PostgreSQL

The real load used `source/03_load_real_catalog.py`, database `sideflix` on `127.0.0.1`. It produced six real movies with six distinct IMDb identifiers, positive runtimes and `imdb` provenance. The earlier catalog of six fictional items was retained in `lab.catalog_reference`; the original files were unchanged at this step.

First pass: six updates. Replay: zero changes and identical `updated_at` values. Primary key and positive-runtime constraints were checked with rejected attempts followed by rollback. The `updated_at` trigger was checked with a change rolled back using `ROLLBACK`. No test data persisted. Evidence kept in this repository: the reviewed input [`source/catalog_real.csv`](../../source/catalog_real.csv) and the later Compose seed output `CATALOGUE_OK rows=6 distinct_imdb=6 changed=6` ([orchestration_report.md](../05_orchestration/orchestration_report.md)). The constraint and trigger checks used prototype scripts that were later removed; their output is not part of this folder.

At this historical step, the data had not yet been loaded into Snowflake; the subsequent step 5 report records that load. Each member can reproduce the local load as in the lab.

Verified catalog:

- A: Whiplash, 6,360 seconds, `tt2582802`
- B: Moonlight, 6,660 seconds, `tt4975722`
- C: Frances Ha, 5,160 seconds, `tt2347569`
- D: Room, 7,080 seconds, `tt3170832`
- E: Sicario, 7,260 seconds, `tt3397884`
- F: Get Out, 6,240 seconds, `tt5052448`

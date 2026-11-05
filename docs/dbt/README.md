# dbt documentation and lineage

This folder contains the dbt documentation generated from the delivered code on 5 November 2026 with `dbt docs generate --static` (dbt Core 1.11.16, dbt-snowflake 1.11.6), run inside the project's `sideflix-dbt:1.0.0` image under the limited `SIDEFLIX_RUNNER` role. The catalog (column types and table statistics) was read from the live Snowflake account at that time. It covers 7 Bronze sources, 11 models (9 Silver views and 2 Gold tables), 21 data tests and the run-results hook.

- `index.html` is a self-contained static site: the manifest and catalog are embedded in it. GitHub shows HTML files as source code, so download or clone the repository and open `docs/dbt/index.html` directly in a browser. Select a model, then open its lineage graph with the button at the bottom right. No Snowflake credentials are needed.
- `manifest.json` and `catalog.json` are the matching machine-readable artifacts from the same run.

For a quick view on GitHub, use [the lineage image](../dbt_lineage.png), [the dbt project README](../../dbt/sideflix_dbt/README.md), and the model and column descriptions in the YAML files under `dbt/sideflix_dbt/models/`.

To regenerate the documentation against the account with an authorized user, using the environment-based Core profile:

```sh
dbt docs generate --static --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
```

Then copy `static_index.html` (renamed `index.html`), `manifest.json` and `catalog.json` from the dbt target folder into `docs/dbt/`. Keep keys and environment files private. The packaged catalog is a dated snapshot, not a live view of the account.

# dbt documentation and lineage

This directory packages the real generated dbt documentation (`index.html`, `manifest.json`, `catalog.json`) from the project's 4 November execution. Model/source descriptions and source-code displays have been refreshed from the submitted English model files; the captured database catalog and dependency graph are preserved. This documentation packaging does not claim a new Snowflake/dbt execution.

GitHub shows HTML as source. After cloning/downloading the repository, run from the repository root:

```sh
python -m http.server 8001 --bind 127.0.0.1
```

Open [the local dbt documentation](http://127.0.0.1:8001/docs/dbt/). Select a model and open its lineage graph. Stop the server with Ctrl+C. No Snowflake credentials are required to browse this saved documentation.

For an immediate GitHub preview, use [the lineage image](../dbt_lineage.png), [the dbt project README](../../dbt/sideflix_dbt/README.md), and the YAML model/column descriptions under `dbt/sideflix_dbt/models/`.

To regenerate against the account using an authorized user and the environment-based Core profile:

```sh
dbt docs generate --project-dir dbt/sideflix_dbt --profiles-dir dbt/profiles-core
```

Keep keys and environment files private. The packaged catalog is a dated execution snapshot, not a live view of the account.

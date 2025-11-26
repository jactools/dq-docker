```markdown
# dbt-databricks

- Install extra: `.[dbt_databricks]` (package: `dbt-databricks`)
- Credentials: Databricks host and token (set `DATABRICKS_HOST` and `DATABRICKS_TOKEN` or provide in `profiles.yml`).
- Usage: configure a `databricks` target in `profiles.yml`; ensure the cluster/user has required permissions.
- Caveats: adapter version must match `dbt-core` compatibility; Databricks runtime and cluster configs affect behavior.

Example `profiles.yml` snippet (Databricks):

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: databricks
      catalog: hive_metastore
      schema: analytics
      host: {{ env_var('DATABRICKS_HOST') }}
      token: {{ env_var('DATABRICKS_TOKEN') }}
```

```
# dbt-databricks

- Install extra: `.[dbt_databricks]` (package: `dbt-databricks`)
- Credentials: Databricks host and token (set `DATABRICKS_HOST` and `DATABRICKS_TOKEN` or provide in `profiles.yml`).
- Usage: configure a `databricks` target in `profiles.yml`; ensure the cluster/user has required permissions.
- Caveats: adapter version must match `dbt-core` compatibility; Databricks runtime and cluster configs affect behavior.

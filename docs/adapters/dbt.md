```markdown
# dbt core

- Install extra: `.[dbt]` (package: `dbt-core`)
- Quick start: after installing `dbt-core` and an adapter (e.g. `dbt-postgres`), run `dbt init` or `dbt debug` to validate the environment.
- Caveats: `dbt-core` has many optional adapters; installing `dbt-core` alone does not provide a connection adapter.

Example `profiles.yml` minimal snippet (Postgres adapter):

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: myuser
      pass: mypass
      port: 5432
      dbname: mydb
      schema: public
```

Example: run dbt debug after installing an adapter:

```bash
pip install -e '.[dbt,dbt_postgres]'
dbt debug
```

```
# dbt core

- Install extra: `.[dbt]` (package: `dbt-core`)
- Quick start: after installing `dbt-core` and an adapter (e.g. `dbt-postgres`), run `dbt init` or `dbt debug` to validate the environment.
- Caveats: `dbt-core` has many optional adapters; installing `dbt-core` alone does not provide a connection adapter.

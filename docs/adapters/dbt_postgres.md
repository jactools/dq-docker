```markdown
# dbt-postgres

- Install extra: `.[dbt_postgres]` (package: `dbt-postgres`)
- Credentials: provide `host`, `user`, `password`, `port`, and `dbname` in `profiles.yml` or via environment variables.
- Usage: after installing `dbt-postgres`, add a `postgres` target to `profiles.yml` and run `dbt debug` to validate.
- Caveats: ensure the adapter version matches `dbt-core`; watch for driver (psycopg2) requirements in CI images.

Example `profiles.yml` snippet (dbt-postgres):

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: {{ env_var('DB_HOST') }}
      user: {{ env_var('DB_USER') }}
      pass: {{ env_var('DB_PASS') }}
      port: 5432
      dbname: mydb
      schema: public
```

```
# dbt-postgres

- Install extra: `.[dbt_postgres]` (package: `dbt-postgres`)
- Credentials: provide `host`, `user`, `password`, `port`, and `dbname` in `profiles.yml` or via environment variables.
- Usage: after installing `dbt-postgres`, add a `postgres` target to `profiles.yml` and run `dbt debug` to validate.
- Caveats: ensure the adapter version matches `dbt-core`; watch for driver (psycopg2) requirements in CI images.

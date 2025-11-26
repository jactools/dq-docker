```markdown
# dbt-redshift

- Install extra: `.[dbt_redshift]` (package: `dbt-redshift`)
- Credentials: Redshift host, user, password, port, and database; configure in `profiles.yml`.
- Usage: ensure proper network access (VPC, security groups), and that the Redshift user has needed privileges.
- Caveats: consider using IAM roles for redshift spectrum/external tables; adapter version must match `dbt-core`.

Example `profiles.yml` snippet (dbt-redshift):

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: redshift
      host: {{ env_var('REDSHIFT_HOST') }}
      user: {{ env_var('REDSHIFT_USER') }}
      password: {{ env_var('REDSHIFT_PASS') }}
      port: 5439
      dbname: mydb
      schema: analytics
```

```
# dbt-redshift

- Install extra: `.[dbt_redshift]` (package: `dbt-redshift`)
- Credentials: Redshift host, user, password, port, and database; configure in `profiles.yml`.
- Usage: ensure proper network access (VPC, security groups), and that the Redshift user has needed privileges.
- Caveats: consider using IAM roles for redshift spectrum/external tables; adapter version must match `dbt-core`.

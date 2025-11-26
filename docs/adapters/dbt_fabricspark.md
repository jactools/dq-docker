```markdown
# dbt-fabricspark

- Install extra: `.[dbt_fabricspark]` (package: `dbt-fabricspark`)
- Credentials: similar to `dbt-fabric` — configure the target in `profiles.yml` with endpoint and auth details.
- Usage & caveats: ensure compatibility between the adapter, Fabric runtime, and `dbt-core`; follow adapter docs for cluster configuration.

Example `profiles.yml` snippet (fabricspark):

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: fabricspark
      host: {{ env_var('FABRIC_HOST') }}
      token: {{ env_var('FABRIC_TOKEN') }}
      schema: analytics
```

```
# dbt-fabricspark

- Install extra: `.[dbt_fabricspark]` (package: `dbt-fabricspark`)
- Credentials: similar to `dbt-fabric` — configure the target in `profiles.yml` with endpoint and auth details.
- Usage & caveats: ensure compatibility between the adapter, Fabric runtime, and `dbt-core`; follow adapter docs for cluster configuration.

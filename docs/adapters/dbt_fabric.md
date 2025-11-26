```markdown
# dbt-fabric

- Install extra: `.[dbt_fabric]` (package: `dbt-fabric`)
- Credentials: Fabric configuration typically requires a Fabric endpoint/host and auth token configured in `profiles.yml`.
- Usage: refer to `dbt-fabric` docs for `profiles.yml` examples; run `dbt debug` to confirm connectivity.
- Caveats: adapter-specific configuration and permissions are required; consult adapter docs.

Example `profiles.yml` snippet (fabric):

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: fabric
      host: {{ env_var('FABRIC_HOST') }}
      token: {{ env_var('FABRIC_TOKEN') }}
      schema: analytics
```

```
# dbt-fabric

- Install extra: `.[dbt_fabric]` (package: `dbt-fabric`)
- Credentials: Fabric configuration typically requires a Fabric endpoint/host and auth token configured in `profiles.yml`.
- Usage: refer to `dbt-fabric` docs for `profiles.yml` examples; run `dbt debug` to confirm connectivity.
- Caveats: adapter-specific configuration and permissions are required; consult adapter docs.

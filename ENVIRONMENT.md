# Environment variables

This file documents environment variables used by the project, whether
they are required, default values, and where they are referenced.

## Important runtime variables

- `DQ_DATA_SOURCE` (required)
  - Purpose: selects the per-data-source YAML mapping under `dq_docker/config/data_sources/`.
  - Default: none — the runtime requires this to be set and will raise at import time when importing `dq_docker.config.gx_config`.
  - Referenced in: `dq_docker/config/gx_config.py`, `docker-compose.prod.yml`, `CONTRIBUTING.md`, `README.md`, various tests.

- `DQ_PROJECT_ROOT` (optional)
  - Purpose: override the detected project root (useful when running inside containers).
  - Default: computed repository root (two levels up from `dq_docker/config`).
  - Referenced in: `dq_docker/config/gx_config.py`, `docker-entrypoint.sh`, `Dockerfile`, `README.md`.

- `DQ_CMD` (optional)
  - Purpose: module path to run inside the container via `python -m $DQ_CMD` (controls container entrypoint behavior).
  - Default: `dq_docker.version_info_cli` (in `Dockerfile` / entrypoint).
  - Referenced in: `Dockerfile`, `docker-compose.yml`, `docker-entrypoint.sh`, `README.md`.

- `DQ_LOG_LEVEL` (optional)
  - Purpose: controls logging level for `dq_docker` (`INFO`/`DEBUG` etc.).
  - Default: `INFO`.
  - Referenced in: `dq_docker/logs/__init__.py`.

- `DQ_RUN_NAME` (optional)
  - Purpose: provide a human-friendly run name that will be persisted into Great Expectations validation metadata (visible in Data Docs under `meta.run_id.run_name`). Useful for correlating runs to releases, CI jobs, or ticket IDs.
  - Default: runtime generates a deterministic fallback name when not provided.
  - Referenced in: `dq_docker/validator.py`, `dq_docker/checkpoint.py`, `docs/runtime.md`.

- `GE_STORE_ACTION` (optional)
  - Purpose: controls defensive Great Expectations store actions on startup to handle stale or corrupted store entries that may trigger pydantic deserialization errors.
  - Allowed values: `none` (default), `repair`, `clear`.
  - Behavior: when set to `repair` the runtime will attempt best-effort reconciliation of store entries that fail to deserialize; when set to `clear` the runtime will remove store entries that cause failures. Use with care in production — prefer `repair` first.
  - Referenced in: `scripts/manage_ge_store.py`, `dq_docker/context.py`, startup/shim logic in `runit.sh` / entrypoint.

- `RUN_ADLS_TESTS` (CI only)
  - Purpose: when set to `true` in CI jobs, instructs workflows to install ADLS optional extras (`requirements-adls.txt`) and run ADLS integration tests. This keeps default CI runs lightweight while allowing opt-in integration testing.
  - Default: `false` / unset.
  - Referenced in: `.github/workflows/ci.yml`.


## Notes for CI and tooling

  - The increment-version script and other CI helpers should not import
  package modules that require runtime environment variables (for
  example `dq_docker.config.gx_config`) at import time. Use
  `scripts/validate_env.py` to verify required variables in CI jobs
  before running steps that depend on them.

## How to validate locally

Use the provided script to assert required variables are set:

```bash
python scripts/validate_env.py
```

Notes:

- To surface `DQ_RUN_NAME` in Data Docs set `DQ_RUN_NAME` before invoking the runtime, for example:

```bash
DQ_RUN_NAME="release-2025-11-28" python -m dq_docker.run_adls_checkpoint
```

- The repository intentionally excludes the `gx/` directory from the final container image via `.dockerignore` and Dockerfile patterns to avoid baking developer-specific Great Expectations artifacts into production images.

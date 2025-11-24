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

# dq_docker

Lightweight project to run data-quality checks with Great Expectations inside Docker.

# dq_docker

Lightweight project to run data-quality checks with Great Expectations inside Docker.

Overview
- Project package: `dq_docker` — contains the runtime entrypoint and namespaced configuration at `dq_docker.config`.
- Local Great Expectations assets (expectations, checkpoints, sample data) live in `dq_great_expectations/` to avoid shadowing the upstream `great_expectations` package.

Quick start
1. Build (Docker):

  # dq_docker

  Lightweight toolkit for running data-quality checks with Great Expectations inside Docker.

  Overview
  - Package: `dq_docker` — runtime entrypoint, configuration (`dq_docker.config`), logging helpers, and utilities.
  - Local GE project: `dq_great_expectations/` contains expectations, checkpoints, and sample data used by the runtime.
  - Contracts: Expectation suites are driven from JSON Open Data Contracts (ODCS) placed under `contracts/`.

  Quick start (local)
  1. Build the container (optional):

     ```bash
     ./buildit.sh
     ```

  2. Run the runtime locally (recommended for development):

     ```bash
     # from project root
     python -m dq_docker.run_adls_checkpoint
     ```

  3. Run in the container using the included helper:

     ```bash
     ./runit.sh
     ```

  Running alternative commands
  - The container and runtime support selecting the module to run via the `DQ_CMD` environment variable (default: `dq_docker.run_adls_checkpoint`).
  - Override the project root (useful when mounting into the container) with `DQ_PROJECT_ROOT`.

  Example (Docker):

  ```bash
  # run the default runtime module and point to a mounted project root
  docker run --rm -e DQ_CMD=dq_docker.run_adls_checkpoint -e DQ_PROJECT_ROOT=/usr/src/app -v "$PWD":/usr/src/app <image>
  ```

  Contracts / Expectations
  - Expectation suites are created from ODCS-style JSON contracts located in `contracts/` (e.g. `contracts/customers_2019.contract.json`).
  - The runtime computes the contract path for the batch name and requires a valid contract when building the suite. See `dq_docker/data_contract.py` and `dq_docker/odcs_validator.py` for the conversion and validation logic.

  Logging
  - The project uses a centralized logging helper `dq_docker.logs.configure_logging()` and `dq_docker.logs.get_logger()` to ensure logs go to stdout (suitable for containers and CI).

  Testing
  - Tests run without installing Great Expectations; tests monkeypatch a fake `great_expectations` module where needed.

  Run the full test suite:

  ```bash
  PYTHONPATH=. pytest -q
  ```

   New test coverage
   - Added a unit test that verifies `contract_to_suite` produces proper
      `ExpectationConfiguration` objects when GE is available:
      `tests/test_contract_to_suite_expectation_config.py`.
   - Tests are written to skip when Great Expectations is not installed so
      local development and CI runs without GE remain fast and isolated.

  CI / Versioning
  - `pyproject.toml` is the single source of truth for the package version; see `dq_docker/_version.py` for the runtime reader.
  - The repo includes a helper script and workflow to increment the patch version in CI (`.github/scripts/update_pyproject_version.py` and the associated workflow).

  Developer notes
  - `dq_docker/run_adls_checkpoint.py` lazily imports Great Expectations inside `main()` so unit tests can inject a fake `great_expectations` module before import.
   - The runtime will attempt to reuse existing datasources and CSV assets (idempotent asset creation), and will only add a `pandas_filesystem` datasource if the configured name is not already present.
   - Batch definitions are also detected and reused when present; the runtime will only call `add_batch_definition_path` when a matching batch definition (by name or path) is not already available on the asset. This makes repeated runs safe in CI and containerized pipelines.
   - `dq_docker/data_contract.py` now converts expectation dictionaries into Great Expectations' `ExpectationConfiguration` objects before adding them to a suite when GE is available. This prevents AttributeError issues when calling `suite.add_expectation` across different GE versions.

  Contact
# dq_docker

Lightweight toolkit for running data-quality checks with Great Expectations inside Docker.

## Overview

- Package: `dq_docker` — runtime entrypoint, configuration (`dq_docker.config`), logging helpers, and utilities.
- Local GE project: `gx/` (or `dq_great_expectations/`) contains expectations, checkpoints, and sample data used by the runtime.
- Contracts: Expectation suites are produced from JSON Open Data Contracts (ODCS) placed under `contracts/`.

## Quickstart (local)

1. Run the runtime locally (recommended for development):

```bash
# from project root
python -m dq_docker.run_adls_checkpoint
```

2. Build and run in Docker (optional):

```bash
./buildit.sh
./runit.sh
# or run directly with docker
docker run --rm -e DQ_CMD=dq_docker.run_adls_checkpoint -e DQ_PROJECT_ROOT=/usr/src/app -v "$PWD":/usr/src/app <image>
```

## Testing

- Tests are designed to run without installing Great Expectations; many tests monkeypatch a fake `great_expectations` module when needed.
- Run the full test suite locally:

```bash
PYTHONPATH=. pytest -q
```

## Developer notes

- Lazy GE imports: runtime functions that interact with Great Expectations import GE lazily at function-runtime. This allows the test suite to inject a fake `great_expectations` module before those imports.
- Module-level helpers: several helper functions (e.g., `get_context`, `ensure_data_docs_site`, `get_batch_and_preview`) are imported at module level in `dq_docker/run_adls_checkpoint.py` so unit tests can monkeypatch them easily.
- Idempotent runtime: the runtime attempts to reuse existing datasources, assets, batch definitions, and validation/checkpoint objects rather than creating duplicates. This makes repeated runs safe in CI and containers.
- Contract-driven suites: expectation suites are built from ODCS contracts via `dq_docker/data_contract.py`. The code constructs `ExpectationConfiguration` objects when GE is available to maintain compatibility across GE versions.

## CI & Versioning

- `pyproject.toml` is the single source of truth for the package version. See `dq_docker/_version.py` for the reader used at runtime.
- The repo includes a helper script and workflow to bump the patch version in CI: `.github/scripts/update_pyproject_version.py` and `.github/workflows/*`.

## Serving Data Docs (nginx)

1. Run the runtime to generate/update Data Docs.

```bash
python -m dq_docker.run_adls_checkpoint
```

2. Start the included nginx container (from project root):

```bash
docker compose -f docker/docker-compose.yml up -d
# then browse http://localhost:8080
```

Notes

- If Data Docs are placed in a non-standard location, update `docker/docker-compose.yml` accordingly.
- See `RELEASE_NOTES.md` for recent changes.

## Contact

- Repository owner: `jactools`

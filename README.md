# dq_docker

Lightweight project to run data-quality checks with Great Expectations inside Docker.

# dq_docker

Lightweight project to run data-quality checks with Great Expectations inside Docker.

Overview
- Project package: `dq_docker` — contains the runtime entrypoint and namespaced configuration at `dq_docker.config`.
- Local Great Expectations assets (expectations, checkpoints, sample data) live in `dq_great_expectations/` to avoid shadowing the upstream `great_expectations` package.

Quick start
1. Build (Docker):

   ```bash
   ./buildit.sh
  # dq_docker

  Lightweight toolkit for running data-quality checks with Great Expectations inside Docker.

  **Overview**
  - Package: `dq_docker` — runtime entrypoint, configuration (`dq_docker.config`), logging helpers, and utilities.
  - Local GE project: `dq_great_expectations/` contains expectations, checkpoints, and sample data used by the runtime.
  - Contracts: Expectation suites are driven from JSON Open Data Contracts (ODCS) placed under `contracts/`.

  **Quick start (local)**
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

  **Running alternative commands**
  - The container and runtime support selecting the module to run via the `DQ_CMD` environment variable (default: `dq_docker.run_adls_checkpoint`).
  - Override the project root (useful when mounting into the container) with `DQ_PROJECT_ROOT`.

  Example (Docker):

  ```bash
  # run the default runtime module and point to a mounted project root
  docker run --rm -e DQ_CMD=dq_docker.run_adls_checkpoint -e DQ_PROJECT_ROOT=/usr/src/app -v "$PWD":/usr/src/app <image>
  ```

  **Contracts / Expectations**
  - Expectation suites are created from ODCS-style JSON contracts located in `contracts/` (e.g. `contracts/customers_2019.contract.json`).
  - The runtime computes the contract path for the batch name and requires a valid contract when building the suite. See `dq_docker/data_contract.py` and `dq_docker/odcs_validator.py` for the conversion and validation logic.

  **Logging**
  - The project uses a centralized logging helper `dq_docker.logs.configure_logging()` and `dq_docker.logs.get_logger()` to ensure logs go to stdout (suitable for containers and CI).

  **Testing**
  - Tests run without installing Great Expectations; tests monkeypatch a fake `great_expectations` module where needed.

  Run the full test suite:

  ```bash
  PYTHONPATH=. pytest -q
  ```

  **CI / Versioning**
  - `pyproject.toml` is the single source of truth for the package version; see `dq_docker/_version.py` for the runtime reader.
  - The repo includes a helper script and workflow to increment the patch version in CI (`.github/scripts/update_pyproject_version.py` and the associated workflow).

  **Developer notes**
  - `dq_docker/run_adls_checkpoint.py` lazily imports Great Expectations inside `main()` so unit tests can inject a fake `great_expectations` module before import.
  - The runtime will attempt to reuse existing datasources and CSV assets (idempotent asset creation), and will only add a `pandas_filesystem` datasource if the configured name is not already present.

  **Contact**
  - Repository owner: `jactools`

  ***

  See `RELEASE_NOTES.md` for recent changes and upgrade notes.

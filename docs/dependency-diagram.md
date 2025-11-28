<!-- Dependency diagram for dq_docker package generated as Mermaid markup -->

# dq_docker dependency diagram

```mermaid
flowchart LR
  %% Core runtime
  run["run_adls_checkpoint"]

  %% Helpers & modules
  expectations["expectations"]
  data_contract["data_contract"]
  odcs_validator["odcs_validator"]
  data_source["data_source"]
  batch_def["batch_definition"]
  suite["expectation_suite"]
  validation["validation_definition"]
  checkpoint["checkpoint"]
  data_docs["data_docs"]
  context_mod["context"]
  logs["logs"]
  config_gx["config.gx_config"]
  version_cli["version_info_cli"]
  pkg_init["__init__"]
  version_mod["_version"]

  %% runtime dependencies
  run -->|uses| expectations
  run -->|uses| data_source
  run -->|uses| batch_def
  run -->|uses| suite
  run -->|uses| validation
  run -->|uses| checkpoint
  run -->|reads config| config_gx
  run -->|initializes| data_docs
  run -->|gets context| context_mod
  run -->|logging| logs

  %% expectations -> contract -> validator
  expectations -->|builds suites via| data_contract
  data_contract -->|validates via| odcs_validator

  %% modules that use logging
  data_source -->|logging| logs
  batch_def -->|logging| logs
  suite -->|logging| logs
  validation -->|logging| logs
  checkpoint -->|logging| logs
  data_docs -->|logging| logs
  context_mod -->|logging| logs
  version_cli -->|logging| logs

  %% package metadata
  pkg_init -->|imports| config_gx
  pkg_init -->|reads| version_mod
  version_cli -->|reads| version_mod

  style run fill:#f9f,stroke:#333,stroke-width:1px
  style expectations fill:#fffbcc
  style data_contract fill:#fffbcc
  style odcs_validator fill:#ffe6cc
  style data_source fill:#e6fff2
  style batch_def fill:#e6fff2
  style suite fill:#e6fff2
  style validation fill:#e6fff2
  style checkpoint fill:#e6fff2
  style data_docs fill:#e6fff2
  style context_mod fill:#e6fff2
  style logs fill:#d9e7ff
  style config_adls fill:#f0f0f0
  style pkg_init fill:#f0f0f0
  style version_mod fill:#f0f0f0
  style version_cli fill:#f0f0f0

```

Notes
- This diagram shows internal module dependencies within the `dq_docker` package (only intra-package imports and relations). It intentionally omits external libraries (Great Expectations, Azure SDKs, Pandas) for clarity.

External dependencies and extras

- Core runtime deps: `requirements.txt` — generated from `pyproject.toml` and used for normal runtime images.
- Dev deps: `requirements-dev.txt` — development and test dependencies used by CI and local development environments.
- ADLS extras: `requirements-adls.txt` — optional dependencies required for Azure Data Lake Storage (adlfs/fsspec). CI installs this file only when `RUN_ADLS_TESTS=true` to keep default CI runs lightweight.
- Delta extras: `requirements-delta.txt` — optional dependencies for Delta Lake (`deltalake`, `pyarrow`) when needed.

Notes on packaging & CI

- The repository generates pinned `requirements*.txt` files from `pyproject.toml` using `.github/scripts/generate_requirements.py`. Keep `pyproject.toml` canonical; regenerate requirements when you update dependencies.
- The `Dockerfile` and `buildit.sh` support selecting a requirements file via the build-arg/ENV `REQUIREMENTS_FILE` so you can build a slim runtime image or a dev image with extra packages.
- To avoid accidentally baking local Great Expectations artifacts into production images, the repo excludes `gx/` via `.dockerignore` and Dockerfile build patterns; mount `gx/` at runtime for development workflows.

If you maintain or change extras, update `requirements-*.txt` and verify CI with `RUN_ADLS_TESTS=true` when ADLS changes are relevant.

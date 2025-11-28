# dq_docker

Version: 0.2.21

Local GE project: `gx/` contains expectations, checkpoints, and sample data used by the runtime. The repository intentionally avoids baking developer `gx/` artifacts into production images: `.dockerignore` entries and Dockerfile build patterns prevent `gx/` from being copied into final runtime images. For development you can mount the project into a running container to expose local `gx/` content.
Generated Great Expectations artifacts: `gx/uncommitted/` contains data docs and validation artifacts created at runtime. This directory is ignored by default (`.gitignore`). Regenerate Data Docs with the project DataContext (see the "Production build and serve" section below).

Version: 0.2.21

Lightweight toolkit for running data-quality checks with Great Expectations inside Docker.

## Overview

- Package: `dq_docker` — runtime entrypoint, configuration (`dq_docker.config`), logging helpers, and utilities.
- Local GE project: `gx/` contains expectations, checkpoints, and sample data used by the runtime.
- Contracts: Expectation suites are produced from JSON Open Data Contracts (ODCS) placed under `contracts/`.

Documentation

- Runtime behavior and troubleshooting: `docs/runtime.md` — describes `DQ_RUN_NAME`/`run_id` metadata, `GE_STORE_ACTION` startup options, examples, and the `scripts/manage_ge_store.py` CLI for repair/clear operations.

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

#### Choosing which requirements to install in the image

The `Dockerfile` and helper `./buildit.sh` now support selecting which
requirements file is used when installing dependencies into the image. This
allows you to build a development image that includes dev/test packages
(for example `requirements-dev.txt`) or a slimmer runtime image using
`requirements.txt`.

- To build the image using the default `requirements.txt` (recommended for
	runtime images):

```bash
./buildit.sh
```

- To build the image using the `requirements-dev.txt` (includes dev deps):

```bash
./buildit.sh --requirements-file requirements-dev.txt
```

Under the hood the script passes a Docker build-arg `REQUIREMENTS_FILE` to
the `docker compose build` command which populates the `ARG/ENV
REQUIREMENTS_FILE` in the `Dockerfile`. You can also set the environment
variable yourself before running the script:

```bash
export REQUIREMENTS_FILE=requirements-dev.txt
./buildit.sh
```

This ensures the image installs the same pinned `great_expectations` version
and other dependencies declared in your repository requirements files.

### Production build and serve (embed Data Docs)

Data Docs into a dedicated `nginx` image. The repo contains an example CI
workflow and helper scripts to make this easy.

1. Generate Data Docs into `uncommitted/data_docs/local_site` (for example
	 `uncommitted/data_docs/local_site/ds_sample_data`). Customize the
	 generation command to your project; see
	 `.github/workflows/build-with-data-docs.example.yml` for a CI example.

2. Build production images locally (package image + nginx image embedding Data Docs):

```bash
./buildit.sh --prod
```

3. Run production compose (ensure `DQ_DATA_SOURCE` is set):

```bash
export DQ_DATA_SOURCE=ds_sample_data
./runit.sh --prod --serve-docs
# or
DQ_DATA_SOURCE=ds_sample_data docker compose -f docker-compose.prod.yml up -d
```

Notes:
- The `nginx` image that embeds Data Docs is built from
	`docker/nginx/Dockerfile.prod` and will copy the site from
	`uncommitted/data_docs/local_site` into `/usr/share/nginx/html` inside the image.
- In CI prefer copying the generated site into the build workspace and
	building the nginx image there; this produces a single, deployable
	artifact with no runtime mount dependencies.

Note on runtime data-source selection

- By default (when `DQ_DATA_SOURCE` is not set) the runtime will iterate
	all configured data sources in `dq_docker/config/data_sources.yml`
	and run validations for each one in turn. This is useful when you
	want to validate multiple historical batches (for example
	`customers_2019` and `customers_2020`) without selecting a single
	source.

- In production the entrypoint `runit.sh --prod` will emit a warning
	(rather than failing) when `DQ_DATA_SOURCE` is unset and will proceed
	to validate all configured sources. To validate a single source,
	set `DQ_DATA_SOURCE` to the desired source key (for example
	`ds_sample_data`).

Examples:

```bash
export DQ_DATA_SOURCE=ds_sample_data
./buildit.sh --prod
./runit.sh --prod --serve-docs
```


### Environment variables

- `DQ_CMD`: module path to run inside container (default `dq_docker.run_adls_checkpoint`)
- `DQ_PROJECT_ROOT`: path inside container that contains the project root (used by the runtime to locate `gx/`, `contracts/`, etc.)

Additional runtime environment variables

- `DQ_RUN_NAME`: optional human-friendly run name to attach to validation runs and Data Docs. If set, the runtime will use this value as the `run_name` and include it in the generated `run_id` metadata. If not set, the runtime generates a deterministic default run name of the form `<definition_name>-YYYYMMDDTHHMMSSZ`.
- `GE_STORE_ACTION`: controls best-effort store reconciliation at startup. Accepted values:
	- `none` (default): do nothing
	- `repair`: scan DataContext stores and delete any stored `ValidationDefinition` or `Checkpoint` entries that fail to deserialize
	- `clear`: destructive — delete all keys in ValidationDefinition/Checkpoint stores
	- `repair_and_clear` or `clear_and_repair`: combination behavior (order: clear then repair)

These flags are intended to make container startup resilient when the on-disk GE store contains stale or incompatible serialized objects (for example after changing datasources or expectations). Use `GE_STORE_ACTION=repair` in development when you want the runtime to attempt non-destructive cleanup, and prefer `none` for production images unless you intentionally want the runtime to modify the store.

## Contracts / Expectations

- Expectation suites are built from ODCS JSON contract files located in `contracts/`.
- The runtime maps the batch definition name to a contract filename; see `dq_docker/data_contract.py` and `dq_docker/odcs_validator.py` for contract validation and conversion details.

- Canonical contract filenames: the runtime derives the canonical
	contract filename by stripping a trailing year suffix of the form
	`_YYYY` from the batch definition name. Provide contracts under
	`contracts/` using the canonical name (for example
	`contracts/customers.contract.json`) and ensure the contract's
	internal `"name"` field matches the canonical name (for example
	`"customers"`). This avoids maintaining duplicate contract files for
	each year and keeps expectation suites stable.

## Testing

- Unit tests are written with `pytest` and designed to run without a real Great Expectations install by monkeypatching `great_expectations` where needed.
- Run the full test suite:

```bash
PYTHONPATH=. pytest -q
```

For development and CI parity, you can create a local virtualenv and install the real `great_expectations` package (and other dev dependencies) with the included helper script:

```bash
scripts/setup_dev_env.sh
source .venv/bin/activate
pytest -q
```

This ensures the test environment uses the real `great_expectations[azure]` package as declared in `requirements.txt` / `pyproject.toml`.

### Optional data-source extras

If you want to install runtime support for specific data sources, the package exposes optional extras. Install only what you need:

- ADLS Gen2 support (adlfs):

```bash
pip install -e '.[adls]'
```

- Delta Lake reader (deltalake + pyarrow):

```bash
pip install -e '.[delta]'
```

- Install both ADLS + Delta together:

```bash
pip install -e '.[datasources]'
```

Using extras keeps development environments lean and allows engineers to choose only the drivers they need.

- Install everything (all optional data-source packages and readers):

```bash
pip install -e '.[all]'
```

Other data-source extras available:

- Amazon S3 (s3fs):

```bash
pip install -e '.[s3]'
```

- Google Cloud Storage (gcsfs):

```bash
pip install -e '.[gcs]'
```

- BigQuery (google-cloud-bigquery):

```bash
pip install -e '.[bigquery]'
```

- Snowflake (snowflake-connector-python):

```bash
pip install -e '.[snowflake]'
```

- Postgres (psycopg2 + SQLAlchemy):

```bash
pip install -e '.[postgres]'
```

Note: some drivers (e.g., `deltalake`, `pyarrow`, `snowflake-connector-python`, `psycopg2-binary`) may require platform-specific wheels or build tools. For CI and developer machines, prefer installing prebuilt wheels where possible.

- dbt core (for local model compilation/execution):

```bash
pip install -e '.[dbt]'
```

Or install everything including dbt:

```bash
pip install -e '.[all]'
```

DBT adapter extras

You can install individual dbt adapters as extras. Example:

- Databricks adapter:

```bash
pip install -e '.[dbt_databricks]'
```

- Postgres adapter:

```bash
pip install -e '.[dbt_postgres]'
```

- Fabric adapters (fabric / fabricspark):

```bash
pip install -e '.[dbt_fabric]'
pip install -e '.[dbt_fabricspark]'
```

- Redshift adapter:

```bash
pip install -e '.[dbt_redshift]'
```

These adapter extras are also included in `.[all]` if you want a single install that includes dbt and common adapters.

Adapter bundles

To simplify installs, the package exposes grouped adapter bundles:

- SQL adapters (Postgres + Redshift):

```bash
pip install -e '.[dbt_sql_adapters]'
```

- Fabric adapters (fabric + fabricspark):

```bash
pip install -e '.[dbt_fabric_adapters]'
```

- Cloud adapters (Databricks):

```bash
pip install -e '.[dbt_cloud_adapters]'
```

- All dbt adapters (databricks, postgres, fabric, fabricspark, redshift):

```bash
pip install -e '.[dbt_all_adapters]'
```

These bundles are conveniences that group commonly used adapters so engineers can install only the adapters they need.

Adapter documentation

Short adapter notes and credential hints are available in the `docs/adapters/` folder. Use these links for quick setup:

- ADLS Gen2: `docs/adapters/adls.md`
- Amazon S3: `docs/adapters/s3.md`
- Google Cloud Storage: `docs/adapters/gcs.md`
- BigQuery: `docs/adapters/bigquery.md`
- Snowflake: `docs/adapters/snowflake.md`
- Postgres: `docs/adapters/postgres.md`
- dbt core: `docs/adapters/dbt.md`
- dbt-databricks: `docs/adapters/dbt_databricks.md`
- dbt-postgres: `docs/adapters/dbt_postgres.md`
- dbt-fabric: `docs/adapters/dbt_fabric.md`
- dbt-fabricspark: `docs/adapters/dbt_fabricspark.md`
- dbt-redshift: `docs/adapters/dbt_redshift.md`

- Secure examples and CI credential patterns: `docs/adapters/secure.md`

These files contain install hints, common environment variables, and short caveats to help get each adapter working quickly.



CI

- A GitHub Actions workflow `/.github/workflows/ci.yml` runs the test suite on pushes and PRs to `main`.
- The workflow sets up Python 3.9 and installs `pytest` and `great_expectations` before running the test suite.
 - The workflow sets up Python 3.13 and installs `pytest` and `great_expectations` before running the test suite. A new optional CI flag
 	 `RUN_ADLS_TESTS` can be set to `true` to install ADLS extras (`requirements-adls.txt`) and run ADLS integration tests in CI.

Example GitHub Actions job snippet that enables ADLS test setup when `RUN_ADLS_TESTS=true`:

```yaml
- name: Install ADLS extras and run ADLS integration tests
	if: env.RUN_ADLS_TESTS == 'true'
	run: |
		python -m pip install -r requirements-adls.txt
		pytest tests/test_adls_package.py -q
```

Integration smoke tests

- The repo includes a lightweight integration-style test `tests/test_datasource_recreate.py` which asserts the runtime helper recreates a fluent datasource when its configured `base_directory` differs from the runtime `SOURCE_FOLDER` (this guards against container-vs-local path mismatches).

If you want to run tests and also exercise the real GE integration, install `great_expectations[azure]` in your virtualenv before running tests.

## Developer notes

- Lazy GE imports: functions that interact with Great Expectations import GE at runtime (inside functions). This makes unit tests that provide fake GE implementations possible without requiring GE at import time.
- Module-level helpers: `dq_docker/run_adls_checkpoint.py` imports several helpers at module level (e.g., `get_context`, `ensure_data_docs_site`, `get_batch_and_preview`) so unit tests can monkeypatch them.
- Idempotency: runtime helpers attempt to find existing datasources, assets, batch definitions, and validation/checkpoints and reuse them instead of creating duplicates — this makes repeated runs safe.
- Contract-driven suites: expectation suites are built from ODCS contracts via `dq_docker/data_contract.py`. The code constructs `ExpectationConfiguration` objects when GE is available to maintain compatibility across GE versions.

## CI & Versioning

- `pyproject.toml` is the canonical source of the package version.
- CI includes `.github/scripts/update_pyproject_version.py` and workflows to increment the patch version and run tests. The PR workflow installs `toml` so the version script can run.

### Notable changes in this release (0.2.21)

- Preserve `run_name` metadata: the runtime now constructs and passes a typed `RunIdentifier` (when available) into Great Expectations `Checkpoint.run()` so `run_name` is preserved in validation JSON and Data Docs.
- Requirements alignment: `requirements.txt` and optional `requirements-*.txt` files are now generated/reconciled from `pyproject.toml`; see `requirements-adls.txt` and `requirements-delta.txt` for data-source extras.
- CI: optional ADLS extras installation controlled by `RUN_ADLS_TESTS=true` to avoid bloating default CI runs while allowing integration tests when explicitly requested.

## Serving Data Docs (nginx)

After running the runtime, Data Docs are updated under the local GE project (`gx/uncommitted/data_docs/...`). To host them with nginx (included):

```bash
docker compose -f docker/docker-compose.yml up -d
# then browse http://localhost:8080
```

Adjust the mount path in `docker/docker-compose.yml` if your data docs live in a different location.

## Release notes

- See `RELEASE_NOTES.md` for recent changes. The repository uses annotated tags (e.g. `v0.2.2`) to mark releases.

## Troubleshooting

- If tests warn about an imported `great_expectations` raising `ImportError` (pytest deprecation warning), either install a compatible GE package locally or adjust the test that calls `pytest.importorskip` to handle `ImportError` explicitly.

## Contributing

- Fork the repo, implement changes on a feature branch, add tests, and open a PR. Run the test suite locally before opening the PR.

## License

- CC0-1.0 (see repository license file)

## Contact

- Repository owner: `jactools`

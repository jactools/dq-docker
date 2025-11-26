# dq_docker

Version: 0.2.16

Local GE project: `gx/` contains expectations, checkpoints, and sample data used by the runtime.
Generated Great Expectations artifacts: `gx/uncommitted/` contains data docs and validation artifacts created at runtime. This directory is ignored by default (`.gitignore`). Regenerate Data Docs with the project DataContext (see the "Production build and serve" section below).

Version: 0.2.3

Lightweight toolkit for running data-quality checks with Great Expectations inside Docker.

## Overview

- Package: `dq_docker` — runtime entrypoint, configuration (`dq_docker.config`), logging helpers, and utilities.
- Local GE project: `gx/` contains expectations, checkpoints, and sample data used by the runtime.
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

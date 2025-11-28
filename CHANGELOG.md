# Changelog

All notable changes to this project are documented in this file.

## [0.2.21] - 2025-11-28

- Patch release: `0.2.21`.
- Run metadata: preserve and persist a human-friendly `run_name` in Great Expectations validation artifacts by constructing and passing a typed `RunIdentifier` to `Checkpoint.run()` when available; `meta.run_id.run_name` and `meta.run_id.run_time` are now present in persisted validation JSON.
- GE store hardening: added defensive helpers and an interactive management script `scripts/manage_ge_store.py` to repair, reconcile, or clear stale Great Expectations store entries that can trigger pydantic deserialization crashes. Startup can be configured via `GE_STORE_ACTION`.
- Runtime & tooling: added `DQ_RUN_NAME` environment variable to override generated run names and added debug logging around checkpoint execution to aid troubleshooting.
- Docker & CI: ensured `gx/` (local GE project artifacts) is not baked into container images; regenerated `requirements.txt` and `requirements-dev.txt` from `pyproject.toml`; created `requirements-adls.txt` and `requirements-delta.txt` for optional extras. CI installs ADLS extras only when `RUN_ADLS_TESTS=true` to keep default CI runs lightweight.
- Tests: tightened ADLS test guards so integration tests only run when usable credentials are present.
- Docs: added `docs/runtime.md` and updated `README.md` to document run metadata propagation, GE store actions, and CI opt-in behavior.

## [0.2.3] - 2025-11-24

- Patch release: packaging & deployment improvements
- Add `docker-compose.prod.yml` for production deployments without source bind-mounts
- Add `docker/nginx/Dockerfile.prod` and `docker/nginx/nginx.conf` to embed and serve
  generated Great Expectations Data Docs as a self-contained `nginx` image
- Add `buildit.sh --prod` and `runit.sh --prod` to build and run production images
- Add example CI workflows to generate Data Docs, build package and nginx images,
  and optionally publish to a registry

## [0.2.2] - 2025-11-24

- Patch release: testing & developer ergonomics
- Moved several helper imports to module level in `dq_docker/run_adls_checkpoint.py`
  to improve unit-test monkeypatching and added defensive guards around
  `context.list_data_docs_sites()` for test doubles
- Documentation improvements in `README.md`

## [0.2.1] - 2025-11-20

- Patch release: idempotency and expectation compatibility
- Runtime avoids creating duplicate batch and validation definitions by
  detecting and reusing existing resources
- `dq_docker/data_contract.py` converts expectation dicts to
  `ExpectationConfiguration` objects when Great Expectations is available

## [0.2.0] - 2025-11-21

- Centralized logging via `dq_docker.logs`
- Improved ODCS/contract-to-suite conversion and safer `suite.meta` handling
- Runtime hardening: lazy GE imports at runtime, defensive datasource/asset
  lookups, and idempotent CSV asset creation
- Test coverage expanded; tests run without real GE by using test doubles

## [0.1.1] - 2025-11-20

- Moved runtime into `dq_docker` package and added `main()` entrypoint
- Made `pyproject.toml` the canonical package version source

## [0.1.0] - 2025-11-20

- Introduced namespaced configuration package `dq_docker.config`

---

Notes

- This changelog is derived from `RELEASE_NOTES.md`. Use the release tag names
  (e.g. `v0.2.3`) for publishing and GitHub releases.

## [0.2.17] - 2025-11-26

- Patch release: `0.2.17`.
- ADLS: added `ADLSClient.from_key_vault()` to fetch Azure Key Vault secrets and populate `AZURE_*` environment variables so `adlfs`/`fsspec` can authenticate without embedding credentials in repo files.
- Docs: updated adapter docs with secure Key Vault examples and added `docs/adapters/secure.md` snippets for common secret stores and CI usage.
- Tests & runtime: deferred heavy imports (pandas/deltalake) to function scope and added unit tests for Key Vault integration; updated tests to avoid importing compiled pandas at collection time.
- Fixes: corrected `pyproject.toml` duplicate extras entry and fixed `dq_docker/adls/utils.py` indentation error discovered during testing.

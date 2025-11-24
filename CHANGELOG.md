# Changelog

All notable changes to this project are documented in this file.

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

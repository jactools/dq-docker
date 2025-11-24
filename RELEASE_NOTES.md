```markdown
# Release Notes

## 0.2.3 - 2025-11-24

- **Patch:** bump to `0.2.3`.
- **Production & packaging:** add `docker-compose.prod.yml` and an nginx production image (`docker/nginx/Dockerfile.prod`) to embed generated Great Expectations Data Docs into an nginx image for deployable static hosting. Added `docker/nginx/nginx.conf` to route requests to multiple Data Docs sites under `/usr/share/nginx/html/<site>/` and fall back to each site's `index.html`.
- **Dev tooling:** added `buildit.sh --prod` and `runit.sh --prod` to build and run production images; these scripts validate `DQ_DATA_SOURCE` in prod mode and support starting the `nginx` Data Docs service.
- **CI / Releasing:** added example workflows `.github/workflows/build-with-data-docs.example.yml` and `.github/workflows/ci-build-and-publish.example.yml` showing how to generate Data Docs, build the package image, build the nginx image with embedded Data Docs, and optionally push images to a registry.
- **Docs:** updated `README.md` and `CONTRIBUTING.md` with production build/run instructions and CI guidance.

### Notes

- This patch focuses on packaging and deployment ergonomics: it provides a reproducible CI pattern to produce a single deployable nginx image containing Data Docs so runtime deployments do not depend on host mounts. The repository's existing testing, GE-compatibility and idempotency improvements remain unchanged.

---

## 0.2.2 - 2025-11-24

- **Patch:** bump to `0.2.2`.
- **Testing & Developer ergonomics:** moved several helper imports in `dq_docker/run_adls_checkpoint.py` to module level to make unit tests easier to monkeypatch (notably `get_context`, `ensure_data_docs_site`, `get_data_docs_urls`, and `get_batch_and_preview`). Added a defensive guard around `context.list_data_docs_sites()` so fake contexts used in tests won't raise.
- **Docs:** updated `README.md` with clearer quickstart, testing, and developer notes.

### Notes

- These changes are internal and improve testability and developer experience. Runtime lazy-imports of Great Expectations (used to allow tests to run without GE installed) remain in place.

- **Patch:** bump to `0.2.1`.
- **Idempotency:** runtime now avoids creating duplicate batch definitions and validation definitions by detecting and reusing existing resources when present.
- **ExpectationConfiguration conversion:** `dq_docker/data_contract.py` converts expectation dicts into Great Expectations `ExpectationConfiguration` objects when GE is available, preventing an `AttributeError` from `ExpectationSuite.add_expectation` in some GE versions.
- **Tests:** added `tests/test_contract_to_suite_expectation_config.py` to assert `ExpectationConfiguration` objects are produced; the test skips when GE is not installed.

### Notes

- This is a small patch release that addresses runtime idempotency and cross-version Great Expectations compatibility for expectation objects. All existing behaviors and public entrypoints remain unchanged.

---

## 0.2.0 - 2025-11-21

	- Idempotent batch-definition handling: the runtime now detects and reuses existing batch definitions (by name or path) on assets and only calls `add_batch_definition_path` when a matching batch definition is not present. This prevents duplicate batch definitions on repeated runs.
	- ExpectationConfiguration conversion: `dq_docker/data_contract.py` now converts expectation dictionaries into Great Expectations' `ExpectationConfiguration` objects before adding them to an `ExpectationSuite` when GE is available. This fixes an AttributeError raised by `ExpectationSuite.add_expectation` in some GE versions.
	- New unit test: `tests/test_contract_to_suite_expectation_config.py` verifies that `contract_to_suite` yields `ExpectationConfiguration` instances when GE is installed; the test skips gracefully when GE is absent.

### Migration notes



## 0.1.1 - 2025-11-20


Migration notes:

	- `run_adls_checkpoint.py` -> `python -m dq_docker.run_adls_checkpoint`
    - `config.adls_config` -> `dq_docker.config.gx_config`

This patch is backwards-incompatible for direct imports from the previous top-level `config` module; please update references accordingly.

## 0.1.0 - 2025-11-20


Compatibility notes:


```
# Release Notes

## 0.2.0 - 2025-11-21

- Centralized logging (breaking internal change): `dq_docker.logs` provides `configure_logging()` and `get_logger()`; all modules now use this for consistent stdout logs suitable for containers/CI.
- ODCS and contract improvements: improved contract validation and contract-to-suite conversion, including more synthesized datatype expectations and safer `suite.meta` handling for test doubles.
- Runtime hardening: lazy-import Great Expectations inside `main()` (so tests can inject fake `great_expectations`), defensive datasource/asset lookup across GE versions, and idempotent CSV asset creation to avoid duplicate assets on repeated runs.
- Tests and CI: expanded pytest coverage for `contract_to_suite` and runtime behavior; tests run without a real GE install by monkeypatching `great_expectations` and the full suite passes locally.
- Additional fixes (2025-11-21):
	- Idempotent batch-definition handling: the runtime now detects and reuses existing batch definitions (by name or path) on assets and only calls `add_batch_definition_path` when a matching batch definition is not present. This prevents duplicate batch definitions on repeated runs.
	- ExpectationConfiguration conversion: `dq_docker/data_contract.py` now converts expectation dictionaries into Great Expectations' `ExpectationConfiguration` objects before adding them to an `ExpectationSuite` when GE is available. This fixes an AttributeError raised by `ExpectationSuite.add_expectation` in some GE versions.
	- New unit test: `tests/test_contract_to_suite_expectation_config.py` verifies that `contract_to_suite` yields `ExpectationConfiguration` instances when GE is installed; the test skips gracefully when GE is absent.
- Container experience: `docker-entrypoint.sh` now warns on missing folders instead of creating them, and `Dockerfile` supports `DQ_CMD` and `DQ_PROJECT_ROOT` environment overrides for flexible container runs.

### Migration notes

- No API breaking changes for external callers beyond the packaging move done in previous releases; however, code that relied on import-time access to the real `great_expectations` package should be adapted if it expects runtime imports at module import time.

---

## 0.1.1 - 2025-11-20

- Move runtime into package: `run_adls_checkpoint.py` was moved into the `dq_docker` package and now exposes a `main()` entrypoint. Run as a module with `python -m dq_docker.run_adls_checkpoint`.
- Update `runit.sh` to invoke the module inside the container: `python -m dq_docker.run_adls_checkpoint`.
- Add top-level package `dq_docker` and subpackage `dq_docker.config` to provide a stable import path for configuration.
- Remove the legacy top-level `run_adls_checkpoint.py` and `config/` modules to avoid import ambiguity.
- Minor refactors and documentation updates: added `README.md`, `LICENSE` (CC0), and this `RELEASE_NOTES.md`.
- Make `pyproject.toml` the canonical package version: runtime now reads `[project].version` from `pyproject.toml` so runtime and packaging versions stay in sync. A GitHub Action increments the patch on push.

Migration notes:

	- `run_adls_checkpoint.py` -> `python -m dq_docker.run_adls_checkpoint`
	- `config.adls_config` -> `dq_docker.config.gx_config`

This patch is backwards-incompatible for direct imports from the previous top-level `config` module; please update references accordingly.

## 0.1.0 - 2025-11-20

- Introduced namespaced configuration package `dq_docker.config`.
- Moved `adls_config.py` into `dq_docker/config/gx_config.py`.
- Updated `run_adls_checkpoint.py` to import from `dq_docker.config.gx_config`.
- Removed old top-level `config/` package to avoid duplicate modules.
- Added `RELEASE_NOTES.md` documenting this change.

Compatibility notes:

- If you've been importing from `config.adls_config`, update imports to `dq_docker.config.gx_config`.

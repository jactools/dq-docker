```markdown
# Release Notes

## 0.2.16 - 2025-11-25

- **Chore:** consolidate Great Expectations project into `gx/` and remove legacy `dq_great_expectations/` directory.
- **Docs:** updated `README.md` to reference the new `gx/` layout and note `gx/uncommitted/` is ignored by default.
- **Config:** updated GE and runtime configs to point to `gx/sample_data/customers` and added `gx/uncommitted/` to `.gitignore`.
- **Tests:** updated tests and validated locally.

---

## 0.2.3 - 2025-11-24

- **Patch:** bump to `0.2.3`.
- **Production & packaging:** add `docker-compose.prod.yml` and an nginx production image (`docker/nginx/Dockerfile.prod`) to embed generated Great Expectations Data Docs into an nginx image for deployable static hosting. Added `docker/nginx/nginx.conf` to route requests to multiple Data Docs sites under `/usr/share/nginx/html/<site>/` and fall back to each site's `index.html`.
- **Dev tooling:** added `buildit.sh --prod` and `runit.sh --prod` to build and run production images; these scripts validate `DQ_DATA_SOURCE` in prod mode and support starting the `nginx` Data Docs service.
- **CI / Releasing:** added example workflows `.github/workflows/build-with-data-docs.example.yml` and `.github/workflows/ci-build-and-publish.example.yml` showing how to generate Data Docs, build the package image, build the nginx image with embedded Data Docs, and optionally push images to a registry.
- **Docs:** updated `README.md` and `CONTRIBUTING.md` with production build/run instructions and CI guidance.

## 0.2.9 - 2025-11-24

- **Behavior:** canonical contract filename resolution — the runtime now
	derives the canonical contract name by stripping a trailing `_YYYY`
	suffix from batch definition stems (for example `customers_2019` ->
	`customers`). This avoids maintaining duplicate year-suffixed contract
	files and keeps expectation suites stable.

- **Runtime:** when `DQ_DATA_SOURCE` is unset the runtime will iterate
	and validate all configured data sources (useful for validating
	multiple historical batches). `runit.sh --prod` now warns instead of
	aborting when `DQ_DATA_SOURCE` is unset and will proceed to validate
	all configured sources; set `DQ_DATA_SOURCE` to target a single
	source.

- **Docs:** `README.md` and `CONTRIBUTING.md` updated to document the
	canonical-contract behavior, how to run targeted vs. full validations,
	and local test instructions (`PYTHONPATH=. pytest`).

- **Tests:** unit tests were updated and the full test suite passes
	locally (`23 passed, 1 skipped, 2 warnings`).

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

## 0.2.5 - 2025-11-24

- **Release:** bump to `0.2.5`.
- **Testing & CI:** added a unified GitHub Actions workflow (`.github/workflows/ci.yml`) that installs pinned development dependencies from `requirements-dev.txt`, caches pip, installs the package in editable mode, and runs the full `pytest` suite. Added `requirements.txt` and `requirements-dev.txt` generated from `pyproject.toml` to make CI installs reproducible.
- **Unit & Integration tests:** added several tests to improve coverage and guard regressions:
	- `tests/test_contract_normalization.py` — ensures legacy PascalCase expectation names in contracts are normalized to GE snake_case.
	- `tests/test_datasource_recreate.py` — unit test asserting fluent datasource recreation when `base_directory` mismatches (prevents container vs host path failures).
	- `tests/test_end_to_end_checkpoint.py` — an integration-style smoke test that runs an end-to-end checkpoint and verifies Data Docs are produced; the test skips when a real Great Expectations package isn't available (so unit test runs remain fast and deterministic).
- **Runtime fixes:** addressed an `IndentationError` in `dq_docker/data_source.py` and improved datasource recreation logic to automatically recreate a pandas_filesystem datasource if its configured `base_directory` differs from runtime `SOURCE_FOLDER` (this reduces friction running GE configs that contain container paths).
- **Contract handling:** added normalization logic in `dq_docker/data_contract.py` to convert Pascal/CamelCase expectation names to snake_case before constructing GE expectation configs, preventing ExpectationNotFound errors when ingesting legacy contract formats.
- **Packaging:** pinned `great_expectations[azure]==1.8.1` and constrained `pandas>=1.3,<2` in `pyproject.toml` to lock to a known-compatible runtime matrix.

### Notes

- The new tests increase confidence when refactoring GE interactions. The integration smoke test is intentionally conservative and will be skipped if Great Expectations is not installed; CI runs the full integration test because the workflow installs dev dependencies.
- Consider adding a locked `requirements-locked.txt` (fully pinned transitive deps) if you want fully reproducible environment installs in CI and builds.

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

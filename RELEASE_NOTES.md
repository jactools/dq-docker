# Release Notes

## 0.2.0 - 2025-11-21

- Centralized logging (breaking internal change): `dq_docker.logs` provides `configure_logging()` and `get_logger()`; all modules now use this for consistent stdout logs suitable for containers/CI.
- ODCS and contract improvements: improved contract validation and contract-to-suite conversion, including more synthesized datatype expectations and safer `suite.meta` handling for test doubles.
- Runtime hardening: lazy-import Great Expectations inside `main()` (so tests can inject fake `great_expectations`), defensive datasource/asset lookup across GE versions, and idempotent CSV asset creation to avoid duplicate assets on repeated runs.
- Tests and CI: expanded pytest coverage for `contract_to_suite` and runtime behavior; tests run without a real GE install by monkeypatching `great_expectations` and the full suite passes locally.
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
	- `config.adls_config` -> `dq_docker.config.adls_config`

This patch is backwards-incompatible for direct imports from the previous top-level `config` module; please update references accordingly.

## 0.1.0 - 2025-11-20

- Introduced namespaced configuration package `dq_docker.config`.
- Moved `adls_config.py` into `dq_docker/config/adls_config.py`.
- Updated `run_adls_checkpoint.py` to import from `dq_docker.config.adls_config`.
- Removed old top-level `config/` package to avoid duplicate modules.
- Added `RELEASE_NOTES.md` documenting this change.

Compatibility notes:

- If you've been importing from `config.adls_config`, update imports to `dq_docker.config.adls_config`.

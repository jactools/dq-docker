# Release Notes

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

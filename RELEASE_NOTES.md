# Release Notes

## 0.1.0 - 2025-11-20

- Introduced namespaced configuration package `dq_docker.config`.
- Moved `adls_config.py` into `dq_docker/config/adls_config.py`.
- Updated `run_adls_checkpoint.py` to import from `dq_docker.config.adls_config`.
- Removed old top-level `config/` package to avoid duplicate modules.
- Added `RELEASE_NOTES.md` documenting this change.

Compatibility notes:
- If you've been importing from `config.adls_config`, update imports to `dq_docker.config.adls_config`.

# dq_docker

Lightweight project to run data-quality checks with Great Expectations inside Docker.

# dq_docker

Lightweight project to run data-quality checks with Great Expectations inside Docker.

Overview
- Project package: `dq_docker` — contains the runtime entrypoint and namespaced configuration at `dq_docker.config`.
- Local Great Expectations assets (expectations, checkpoints, sample data) live in `dq_great_expectations/` to avoid shadowing the upstream `great_expectations` package.

Quick start
1. Build (Docker):

   ```bash
   ./buildit.sh
   ```

2. Run locally or in the container:

   - Run as module (recommended):

     ```bash
     python -m dq_docker.run_adls_checkpoint
     ```

   - Or use the console script installed from the package (if installed):

     ```bash
     dq-docker-run
     ```

   - To print package + GE versions:

     ```bash
     dq-version
     # or
     python -m dq_docker.version_info_cli
     ```

Notes
- `pyproject.toml` is the single source of truth for the package version; the runtime reads `[project].version` so runtime and packaging stay in sync.
- Local Great Expectations project: `dq_great_expectations/` contains expectations, checkpoints, and sample data used by `dq_docker`.
- Environment variables and secrets are intentionally kept out of the repo (see `.gitignore`).

CI / Versioning
- A GitHub Actions workflow increments the patch version in `pyproject.toml` on push (see `.github/workflows/increment-patch-on-push.yml`). This repository uses `pyproject.toml` as the canonical version file.

Contact
- Repository owner: `jactools`

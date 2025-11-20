# dq_docker

Lightweight project to run data-quality checks with Great Expectations inside Docker.

Overview
- Contains Great Expectations configuration and sample data in `great_expectations/` and `gx/`.
- Includes helper scripts: `buildit.sh`, `runit.sh`, and `run_adls_checkpoint.py`.

Quick start
1. Build (if using Docker):

   ```bash
   ./buildit.sh
   ```

2. Run locally or in the container:

   ```bash
   ./runit.sh
   # or
   python3 run_adls_checkpoint.py
   ```

Notes
- Environment variables are kept out of the repository (`.env` is in `.gitignore`).
- See `great_expectations/` for expectations and sample validation artifacts.

Contact
- Repository owner: `jactools`
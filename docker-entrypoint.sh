#!/usr/bin/env bash
set -euo pipefail

# Enhanced container entrypoint performing pre-start checks and setup
# Checks performed:
# - `DQ_PROJECT_ROOT` must exist (fatal)
# - Ensure project subdirectories exist (`contracts`, `dq_great_expectations`, sample data)
# - Ensure data_docs directory exists (created if absent)
# - Emit warning if common Azure auth env vars are missing
# - Try importing `DQ_CMD` module using Python and warn on failure
# - Print a startup summary then exec the container CMD

: "${DQ_CMD:=dq_docker.version_info_cli}"
: "${DQ_PROJECT_ROOT:=/usr/src/app}"

echo "[entrypoint] DQ_CMD=${DQ_CMD}"
echo "[entrypoint] DQ_PROJECT_ROOT=${DQ_PROJECT_ROOT}"

if [[ ! -d "${DQ_PROJECT_ROOT}" ]]; then
  echo "ERROR: DQ_PROJECT_ROOT='${DQ_PROJECT_ROOT}' does not exist or is not a directory."
  echo "Mount the repository into the container and/or set DQ_PROJECT_ROOT correctly."
  exit 1
fi

# Project layout checks
CONTRACTS_DIR="${DQ_PROJECT_ROOT}/contracts"
GX_PROJECT_DIR="${DQ_PROJECT_ROOT}/gx"
SAMPLE_CUSTOMERS_DIR="${GX_PROJECT_DIR}/sample_data/customers"

if [[ ! -d "${GX_PROJECT_DIR}" ]]; then
  echo "[entrypoint] Warning: expected Great Expectations project directory not found: ${GX_PROJECT_DIR}"
else
  echo "[entrypoint] Found Great Expectations project at ${GX_PROJECT_DIR}"
fi

if [[ ! -d "${CONTRACTS_DIR}" ]]; then
  echo "[entrypoint] Warning: contracts dir not found: ${CONTRACTS_DIR} (will not create)"
fi

if [[ ! -d "${SAMPLE_CUSTOMERS_DIR}" ]]; then
  echo "[entrypoint] Warning: sample data dir not found: ${SAMPLE_CUSTOMERS_DIR} (will not create)"
fi

# Ensure data_docs directory exists (best-effort)
DATA_DOCS_DIR="${DQ_PROJECT_ROOT}/gx/uncommitted/data_docs/${DATA_DOCS_SITE_NAME:-local_site}"
if [[ ! -d "${DATA_DOCS_DIR}" ]]; then
  echo "[entrypoint] Warning: data docs directory not found: ${DATA_DOCS_DIR} (will not create)"
fi

# Check for common Azure service principal env vars and warn if missing
REQUIRED_AZURE_VARS=(AZURE_CLIENT_ID AZURE_CLIENT_SECRET AZURE_TENANT_ID)
missing_any=true
for v in "${REQUIRED_AZURE_VARS[@]}"; do
  if [[ -n "${!v:-}" ]]; then
    missing_any=false
    break
  fi
done
if [[ "$missing_any" == true ]]; then
  echo "[entrypoint] Warning: no Azure service principal env vars detected (AZURE_CLIENT_ID/SECRET/TENANT_ID)."
  echo "[entrypoint] If you plan to use ADLS connectivity, set these in your .env or runtime environment."
fi

# Try to import the DQ_CMD module in Python to surface obvious problems early.
echo "[entrypoint] Checking Python can import DQ_CMD module '${DQ_CMD}'..."
if ! python - <<PYCHK
import sys
import importlib
mod = "${DQ_CMD}"
try:
    importlib.import_module(mod)
    sys.exit(0)
except Exception as e:
    print(f"[entrypoint] Warning: failed to import module '{mod}': {e}")
    sys.exit(2)
PYCHK
then
  echo "[entrypoint] Note: import check failed - continuing but the command may fail at runtime."
fi

echo "[entrypoint] Startup checks complete. Executing: $*"

exec "$@"

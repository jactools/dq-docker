#!/usr/bin/env bash
set -euo pipefail

# Run the runtime container. Supports development (default) and production
# (`--prod`) modes. In development the repo is bind-mounted into the
# container via `docker-compose.yml`. In production the `docker-compose.prod.yml`
# file is used and images are expected to be built (or will be built via
# `buildit.sh --prod`).

SHOW_HELP=0
SERVE_DOCS=1
PROD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --serve-docs)
      SERVE_DOCS=1
      shift
      ;;
    --prod)
      PROD=1
      shift
      ;;
    -h|--help)
      SHOW_HELP=1
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      SHOW_HELP=1
      shift
      ;;
  esac
done

if [[ $SHOW_HELP -eq 1 ]]; then
  sed -n '1,240p' "$0"
  echo
  echo "Usage: $0 [--prod] [--serve-docs]"
  echo "  --prod       Use docker-compose.prod.yml (no repo bind-mounts)."
  echo "  --serve-docs  Start nginx service to serve Data Docs after runtime."
  exit 0
fi

REPO_DIR="$(pwd)"

if [[ ! -f .env ]]; then
  echo "Warning: .env not found in ${REPO_DIR}; create one from .env.example or set environment variables manually."
fi

if [[ $PROD -eq 1 ]]; then
  COMPOSE_FILE="docker-compose.prod.yml"
  echo "Running in PRODUCTION mode using ${COMPOSE_FILE}."

  # Validate required env var for prod: DQ_DATA_SOURCE must be set
  if [[ -z "${DQ_DATA_SOURCE:-}" ]]; then
    echo "Warning: DQ_DATA_SOURCE not set. In production mode the runtime will validate all configured data sources."
    echo "To limit validation to a single source set DQ_DATA_SOURCE to a key from dq_docker/config/data_sources.yml (for example: ds_sample_data)."
    echo "Example: export DQ_DATA_SOURCE=ds_sample_data"
  else
    echo "Validating only data source: ${DQ_DATA_SOURCE}"
  fi

  echo "Bringing up production services via ${COMPOSE_FILE}..."
  docker compose -f ${COMPOSE_FILE} up -d --remove-orphans

  echo "Services started. To view logs: docker compose -f ${COMPOSE_FILE} logs -f"

  RUNTIME_COMPOSE_ARGS=( -f ${COMPOSE_FILE} )
else
  COMPOSE_FILE="docker-compose.yml"
  echo "Running in development mode using ${COMPOSE_FILE} (bind-mounts enabled)."

  echo "Starting runtime via docker compose (service: dq_docker)..."
  docker compose up --build --remove-orphans dq_docker

  echo "Runtime finished."

  RUNTIME_COMPOSE_ARGS=( )
fi

# Optionally start the nginx service to serve Data Docs if requested.
if [[ $SERVE_DOCS -eq 1 ]]; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker not found; cannot start datadocs nginx service."
    exit 0
  fi

  echo "Starting nginx to serve Data Docs via docker compose (${COMPOSE_FILE})..."
  # Start the nginx service if it's defined in the selected compose file; otherwise warn and skip.
  if docker compose ${RUNTIME_COMPOSE_ARGS[@]:-} config --services | grep -q '^nginx$'; then
    if docker compose ${RUNTIME_COMPOSE_ARGS[@]:-} up -d nginx; then
      echo "nginx started and serving Data Docs on http://localhost:8080 (if available)"
    else
      echo "Failed to start nginx via docker compose. Ensure docker compose is available and try:"
      echo "  docker compose -f ${COMPOSE_FILE} up -d nginx"
      exit 1
    fi
  else
    echo "No 'nginx' service defined in ${COMPOSE_FILE}; skipping Data Docs nginx start."
  fi
fi

exit 0

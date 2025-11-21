
#!/usr/bin/env bash
set -euo pipefail

# Run the runtime inside the container. This mounts the repository into
# the container so the package (`dq_docker`) and local Great Expectations
# project (`dq_great_expectations`) are available at runtime. It also
# mounts the data_docs folder so Data Docs updates persist locally.
#
# Usage:
#   ./runit.sh            # run the runtime container
#   ./runit.sh --serve-docs   # run runtime then start nginx to serve Data Docs
# Alternatively set environment variable `DQ_SERVE_DATADOCS=1` to auto-start nginx
# after the runtime completes.

# Requirements:
# - an optional `.env` file in the repo root with necessary environment variables
# - a Docker image named `great-expectations-adls-spn` (built separately)

SHOW_HELP=0
SERVE_DOCS=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --serve-docs)
      SERVE_DOCS=1
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
  sed -n '1,120p' "$0"
  exit 0
fi

REPO_DIR="$(pwd)"

# If a .env file exists, pass it into the container; otherwise warn.
ENV_ARG=()
if [[ -f .env ]]; then
  ENV_ARG=(--env-file .env)
else
  echo "Warning: .env not found in ${REPO_DIR}; continuing without --env-file."
fi

# Ensure the data_docs folder for gx is present (nginx compose mounts gx/uncommitted/data_docs/local_site)
mkdir -p "${REPO_DIR}/gx/uncommitted/data_docs/local_site"

echo "Running runtime container (image: great-expectations-adls-spn)..."
docker run -it --rm \
  "${ENV_ARG[@]}" \
  --volume "${REPO_DIR}:/usr/src/app" \
  --volume "${REPO_DIR}/gx/uncommitted/data_docs:/usr/src/app/gx/uncommitted/data_docs" \
  --volume "${REPO_DIR}/dq_great_expectations/uncommitted/data_docs:/usr/src/app/dq_great_expectations/uncommitted/data_docs" \
  --workdir /usr/src/app \
  great-expectations-adls-spn \
  python -m dq_docker.run_adls_checkpoint

echo "Runtime finished."

# Allow environment override or CLI flag to start nginx to serve Data Docs.
if [[ $SERVE_DOCS -eq 0 && "${DQ_SERVE_DATADOCS-}" == "1" ]]; then
  SERVE_DOCS=1
fi

if [[ $SERVE_DOCS -eq 1 ]]; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker not found; cannot start datadocs nginx service."
    exit 0
  fi

  echo "Starting nginx to serve Data Docs (docker compose -f docker/docker-compose.yml up -d)..."
  if docker compose -f docker/docker-compose.yml up -d; then
    echo "nginx started and serving Data Docs on http://localhost:8080 (if available)"
  else
    echo "Failed to start nginx via docker compose. Ensure docker compose is available and try:"
    echo "  docker compose -f docker/docker-compose.yml up -d"
    exit 1
  fi
fi

exit 0


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

# If a .env file exists, docker-compose will automatically load it when
# using the `env_file` directive in `docker-compose.yml`. We still warn
# if it's missing so developers know to create one.
if [[ ! -f .env ]]; then
  echo "Warning: .env not found in ${REPO_DIR}; create one from .env.example or set environment variables manually."
fi

echo "Starting runtime via docker compose (service: dq_docker)..."

# Bring up the service. We run the container, attach to its logs, and remove
# orphan containers when finished. The compose file mounts the repo for
# development purposes.
docker compose up --build --remove-orphans dq_docker

echo "Runtime finished."

# Optionally start the nginx service to serve Data Docs if requested.
if [[ $SERVE_DOCS -eq 1 ]]; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "docker not found; cannot start datadocs nginx service."
    exit 0
  fi

  echo "Starting nginx to serve Data Docs via docker compose..."
  # Start the nginx service if it's defined in the compose file; otherwise
  # warn and skip.
  if docker compose config --services | grep -q '^nginx$'; then
    if docker compose up -d nginx; then
      echo "nginx started and serving Data Docs on http://localhost:8080 (if available)"
    else
      echo "Failed to start nginx via docker compose. Ensure docker compose is available and try:"
      echo "  docker compose up -d nginx"
      exit 1
    fi
  else
    echo "No 'nginx' service defined in docker-compose.yml; skipping Data Docs nginx start."
  fi
fi

exit 0

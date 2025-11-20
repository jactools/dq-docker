
#!/usr/bin/env bash
set -euo pipefail

# Run the runtime inside the container. This mounts the repository into
# the container so the package (`dq_docker`) and local Great Expectations
# project (`dq_great_expectations`) are available at runtime. It also
# mounts the data_docs folder so Data Docs updates persist locally.
#
# Requirements:
# - an `.env` file in the repo root with necessary environment variables
# - a Docker image named `great-expectations-adls-spn` (built separately)

if [[ ! -f .env ]]; then
  echo "Missing .env file in $(pwd). Create one or pass environment variables another way."
  exit 1
fi

REPO_DIR="$(pwd)"

docker run -it --rm \
  --env-file .env \
  --volume "${REPO_DIR}:/usr/src/app" \
  --volume "${REPO_DIR}/dq_great_expectations/uncommitted/data_docs:/usr/src/app/dq_great_expectations/uncommitted/data_docs" \
  --workdir /usr/src/app \
  great-expectations-adls-spn \
  python -m dq_docker.run_adls_checkpoint

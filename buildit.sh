
#!/usr/bin/env bash
set -euo pipefail

# Build helper for local development and CI. By default this builds the
# development image via `docker compose` using the repository `docker-compose.yml`.
# Use `--prod` to build the production images and the nginx image that embeds
# generated Data Docs (uses `docker-compose.prod.yml` and `docker/nginx/Dockerfile.prod`).

PROD=0

while [[ $# -gt 0 ]]; do
	case "$1" in
		--prod)
			PROD=1
			shift
			;;
		-h|--help)
			echo "Usage: $0 [--prod]"
			echo "  --prod   Build production images (package image + nginx image embedding Data Docs)"
			exit 0
			;;
		*)
			echo "Unknown argument: $1"
			exit 2
			;;
	esac
done

if [[ $PROD -eq 1 ]]; then
	echo "Building production images (package + nginx with embedded Data Docs)..."
	# Build the package image using the repo Dockerfile and the prod compose file
	docker compose -f docker-compose.prod.yml build --pull --no-cache dq_docker || true

	# Build nginx image that embeds generated Data Docs (expects site at uncommitted/data_docs/local_site)
	if [[ -d "uncommitted/data_docs/local_site" ]]; then
		docker build -t jactools/dq-docker-nginx:latest -f docker/nginx/Dockerfile.prod .
		echo "Built jactools/dq-docker-nginx:latest"
	else
		echo "Warning: generated Data Docs not found at ./uncommitted/data_docs/local_site. Skipping nginx image build."
		echo "If you intend to build the nginx image, generate Data Docs into that location first."
	fi

	echo "Production build finished. You can run with: DQ_DATA_SOURCE=<source> docker compose -f docker-compose.prod.yml up -d"
	exit 0
fi

echo "Building docker images via docker compose (development)..."
docker compose build --pull --no-cache dq_docker

echo "Build finished. You can run with: docker compose up --build"



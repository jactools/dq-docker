### Builder stage: build a wheel for the package
FROM python:3.13 AS builder

WORKDIR /src

# Copy source so the wheel can be built inside the image
COPY . /src

# Install build tools and build a wheel into /wheels
RUN python -m pip install --upgrade pip setuptools wheel build \
 && python -m build --wheel --outdir /wheels


### Runtime stage: install runtime deps and the built wheel
FROM python:3.13

# Set environment variables for non-interactive commands
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /usr/src/app

# Allow selecting which requirements file to install. Default is
# `requirements.txt` but this can be overridden with the build-arg or runtime
# env `REQUIREMENTS_FILE`.
ARG REQUIREMENTS_FILE=requirements.txt
ENV REQUIREMENTS_FILE=${REQUIREMENTS_FILE}

# Copy requirements files. We copy both common files so callers can select
# either `requirements.txt` or `requirements-dev.txt` at build/run time.
# Copy any requirements file matching `requirements*.txt` so new/alternate
# requirements files are automatically included without editing the Dockerfile.
COPY requirements*.txt /usr/src/app/

# Copy the wheel from the builder stage and
COPY --from=builder /wheels/*.whl /tmp/

# Copy remaining files (entrypoint, configs, etc.)
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

COPY . /usr/src/app

# Ensure the package root is importable
ENV PYTHONPATH=/usr/src/app

# Default environment variables (can be overridden at `docker run`):
ENV DQ_CMD=dq_docker.version_info_cli
ENV DQ_PROJECT_ROOT=/usr/src/app

# Install runtime dependencies from the selected requirements file. This will
# respect the pinned `great_expectations` version declared in the repo. The
# `REQUIREMENTS_FILE` may be set during `docker build` as `--build-arg` or at
# runtime as an environment variable.
RUN pip install --no-cache-dir -r /usr/src/app/${REQUIREMENTS_FILE}

# install the wheel copied from the builder (no-deps, runtime deps already installed)
RUN pip install --no-cache-dir --no-deps /tmp/*.whl

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["sh", "-c", "python -m ${DQ_CMD}"]

# Use the official Python 3.13 base image from Docker Hub
# 'slim-bookworm' provides a minimal, secure base image based on Debian Bookworm
FROM python:3.13

# Set environment variables for non-interactive commands
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /usr/src/app

# Install the latest version of Great Expectations
RUN pip install --no-cache-dir great_expectations[azure]

# Install necessary libraries for ADLS Gen2 connectivity and data processing
RUN pip install --no-cache-dir azure-storage-file-datalake azure-identity pandas

COPY . /usr/src/app

# Ensure the package root is importable
ENV PYTHONPATH=/usr/src/app

# Default environment variables (can be overridden at `docker run`):
# - `DQ_CMD` : python module to run with `python -m` (default prints package version)
# - `DQ_PROJECT_ROOT`: project root inside container (used by runtime config)
ENV DQ_CMD=dq_docker.version_info_cli
ENV DQ_PROJECT_ROOT=/usr/src/app

# Default command: run the module specified by `DQ_CMD` (shell form expands env vars)
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Entrypoint performs pre-start checks then execs the command
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["sh", "-c", "python -m ${DQ_CMD}"]

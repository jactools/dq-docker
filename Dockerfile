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

# Command to run an example great_expectations command when the container starts
CMD ["python", "great_expectations/version_info.py"]

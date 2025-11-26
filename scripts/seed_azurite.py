"""Seed Azurite with a sample container and a small CSV for local testing.

This script uses `azure-storage-blob` to connect to Azurite using the
standard Azurite connection string. By default it will use the well-known
Azurite devstore account settings if `AZURITE_CONNECTION_STRING` is not set.

Usage:
  python scripts/seed_azurite.py --container mycontainer --file sample.csv

If the file doesn't exist, a small sample CSV will be created and uploaded.
"""
from __future__ import annotations

import argparse
import os
from azure.storage.blob import BlobServiceClient

DEFAULT_AZURITE_CONNECTION = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFeqCnfJ1a==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)


def get_connection_string() -> str:
    return os.environ.get("AZURITE_CONNECTION_STRING", DEFAULT_AZURITE_CONNECTION)


def seed_container(connection_string: str, container: str, local_file: str | None):
    svc = BlobServiceClient.from_connection_string(connection_string)
    container_client = svc.get_container_client(container)
    try:
        container_client.create_container()
        print(f"Created container '{container}'")
    except Exception:
        print(f"Container '{container}' already exists or could not be created (continuing)")

    if not local_file:
        # create a small sample CSV in memory
        local_file = "_tmp_seed_sample.csv"
        with open(local_file, "w") as fh:
            fh.write("id,name\n1,Alice\n2,Bob\n")
        cleanup = True
    else:
        cleanup = False

    blob_client = container_client.get_blob_client(os.path.basename(local_file))
    with open(local_file, "rb") as fh:
        blob_client.upload_blob(fh, overwrite=True)
    print(f"Uploaded {local_file} to container '{container}'")

    if cleanup and os.path.exists(local_file):
        os.remove(local_file)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--container", "-c", default="test-container")
    p.add_argument("--file", "-f", help="Local file to upload. If omitted a small CSV will be created")
    args = p.parse_args()

    conn = get_connection_string()
    seed_container(conn, args.container, args.file)

"""ADLS Gen2 helpers.

Small, framework-agnostic helpers to produce ADLS Gen2 paths and a
recommended set of environment variable names. These are intentionally
lightweight scaffolds — they don't add heavy ADL/azure SDK logic so the
project can choose how to wire authentication (service principal, managed
identity, connection string, etc.).

Usage:
    from dq_docker.adls import adls_path, env_var_names
    path = adls_path(container="mycontainer", path="sample_data/customers")

Notes:
 - To access ADLS Gen2 via pandas/Great Expectations you can use the
   `adlfs`/`fsspec` integration (install `adlfs`) and reference
   `abfs://<container>/path` URIs.
 - Authentication can be provided with env vars or Azure SDK patterns.
"""

from typing import Dict


def adls_path(container: str, path: str = "") -> str:
    """Return a normalized abfs URI for ADLS Gen2.

    Examples:
        adls_path("mycontainer", "data/customers") -> "abfs://mycontainer/data/customers"
    """
    p = path.lstrip("/")
    if p:
        return f"abfs://{container}/{p}"
    return f"abfs://{container}/"


def env_var_names() -> Dict[str, str]:
    """Return recommended environment variable names for ADLS auth.

    These are only recommendations; your deployment may choose different
    variables or secret stores.
    """
    return {
        "account": "AZURE_STORAGE_ACCOUNT_NAME",
        "tenant_id": "AZURE_TENANT_ID",
        "client_id": "AZURE_CLIENT_ID",
        "client_secret": "AZURE_CLIENT_SECRET",
    }

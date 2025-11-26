import os
from typing import List

def build_abfs_uri(container: str, path: str) -> str:
    """Build an `abfs://` URI for ADLS Gen2.

    Example: build_abfs_uri('mycontainer', 'data/file.csv') -> 'abfs://mycontainer/data/file.csv'
    """
    path = path.lstrip("/")
    return f"abfs://{container}/{path}"

def env_var_names() -> List[str]:
    """Return recommended environment variable names for ADLS auth.

    These are suggestions; authentication can also be provided via Managed Identity
    (azure-identity) which adlfs will pick up automatically.
    """
    return [
        "AZURE_STORAGE_ACCOUNT_NAME",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
    ]

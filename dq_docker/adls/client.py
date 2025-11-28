import os
from typing import Optional, Any

from .utils import build_abfs_uri

# Eager imports (remove lazy imports)
import fsspec  # adlfs registers itself as an fsspec implementation
import pandas as pd
from deltalake import DeltaTable


class ADLSClient:
    """Minimal ADLS Gen2 client using fsspec/adlfs.

    Supports reading CSVs and Parquet (and a small helper for Delta tables
    if the optional `deltalake` package is installed).

    This class includes a convenience constructor `from_key_vault` which will
    fetch ADLS-related secrets from Azure Key Vault and populate environment
    variables expected by `adlfs`/`fsspec`. This avoids hardcoding credentials
    in repo files and works with service principals or managed identities.
    """

    def __init__(self, storage_account: Optional[str] = None):
        self.storage_account = storage_account or os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
        if fsspec is None:
            raise RuntimeError("Missing dependency: install adlfs via 'pip install .[adls]' to use ADLSClient")

    @classmethod
    def from_key_vault(
        cls,
        vault_url: str,
        account_name_secret: str = "adls-account-name",
        client_id_secret: str = "adls-client-id",
        client_secret_secret: str = "adls-client-secret",
        tenant_id_secret: str = "adls-tenant-id",
        credential: Optional[object] = None,
    ) -> "ADLSClient":
        """Create an `ADLSClient` by fetching secrets from Azure Key Vault.

        Parameters:
        - `vault_url`: the Key Vault URL, e.g. 'https://my-vault.vault.azure.net/'
        - secret names: defaults shown above. The secret values will be used to
          populate `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`,
          and optionally `AZURE_STORAGE_ACCOUNT_NAME` environment variables.
        - `credential`: optional credential implementing azure.identity credentials

        This method requires `azure-identity` and `azure-keyvault-secrets` to be
        installed in the environment.
        """
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
        except Exception:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Key Vault integration requires 'azure-identity' and 'azure-keyvault-secrets'."
            )

        credential = credential or DefaultAzureCredential()
        sc = SecretClient(vault_url=vault_url, credential=credential)

        # Fetch secrets if present and set env vars so adlfs (fsspec) can pick them up
        try:
            client_id = sc.get_secret(client_id_secret).value
            client_secret = sc.get_secret(client_secret_secret).value
            tenant_id = sc.get_secret(tenant_id_secret).value
        except Exception as exc:  # pragma: no cover - conservative error handling
            raise RuntimeError(f"Failed to fetch Key Vault secrets: {exc}")

        os.environ["AZURE_CLIENT_ID"] = client_id
        os.environ["AZURE_CLIENT_SECRET"] = client_secret
        os.environ["AZURE_TENANT_ID"] = tenant_id

        storage_account = None
        try:
            storage_account = sc.get_secret(account_name_secret).value
            os.environ["AZURE_STORAGE_ACCOUNT_NAME"] = storage_account
        except Exception:
            # account name is optional; if missing we leave AZURE_STORAGE_ACCOUNT_NAME
            # unset and require the caller to provide it or rely on other configuration.
            storage_account = None

        return cls(storage_account=storage_account)

    def path(self, container: str, path: str) -> str:
        return build_abfs_uri(container, path)

    def read_csv(self, container: str, path: str, **kwargs) -> Any:
        """Read a CSV from ADLS into a pandas DataFrame.

        `storage_options` may be provided in kwargs (it will be forwarded to
        the pandas reader when using a URL form supported by fsspec/adlfs).
        """
        import sys

        uri = self.path(container, path)
        storage_options = kwargs.pop("storage_options", {})
        local_pd = sys.modules.get("pandas", pd)
        return local_pd.read_csv(uri, storage_options=storage_options, **kwargs)

    def read_parquet(self, container: str, path: str, **kwargs) -> Any:
        """Read a Parquet or Delta-Parquet file/table from ADLS.

        This uses `fsspec` to open the remote file and `pandas.read_parquet`
        to parse it. For Delta tables, see `read_delta_table` below.
        """
        import sys

        uri = self.path(container, path)
        fs, path_in_fs = fsspec.core.url_to_fs(uri)
        with fs.open(path_in_fs, "rb") as fh:
            local_pd = sys.modules.get("pandas", pd)
            return local_pd.read_parquet(fh, **kwargs)

    def read_delta_table(self, container: str, table_path: str, **kwargs) -> Any:
        """Read a Delta table using the optional `deltalake` package.

        If `deltalake` is not installed a helpful error is raised. If installed,
        this will attempt to read the table and return a pandas DataFrame.
        """
        uri = self.path(container, table_path)
        try:
            dt = DeltaTable(uri)
            return dt.to_pandas(**kwargs)
        except Exception as exc:
            # Normalize errors from the deltalake backend into a RuntimeError
            # so callers receive a consistent message when the table cannot
            # be read (for example when account/credentials are not provided).
            raise RuntimeError(
                "Delta support requires the 'deltalake' package. Install it with 'pip install deltalake'"
            )

        uri = self.path(container, table_path)
        try:
            dt = DeltaTable(uri)
        except Exception as exc:  # normalize deltalake/backend errors for callers
            raise RuntimeError(
                "Failed to load Delta table (deltalake backend error): %s" % exc
            ) from exc
        return dt.to_pandas(**kwargs)

    def list_files(self, container: str, path: str = ""):
        uri = self.path(container, path)
        fs, _ = fsspec.core.url_to_fs(uri)
        prefix = uri.split("//", 1)[1]
        return fs.ls(prefix)

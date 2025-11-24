import os
from typing import Optional

from .utils import build_abfs_uri

try:
    import fsspec  # adlfs registers itself as an fsspec implementation
except Exception:  # pragma: no cover - import-time guard
    fsspec = None

import pandas as pd


class ADLSClient:
    """Minimal ADLS Gen2 client using fsspec/adlfs.

    Supports reading CSVs and Parquet (and a small helper for Delta tables
    if the optional `deltalake` package is installed).
    """

    def __init__(self, storage_account: Optional[str] = None):
        self.storage_account = storage_account or os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
        if fsspec is None:
            raise RuntimeError("Missing dependency: install adlfs via 'pip install .[adls]' to use ADLSClient")

    def path(self, container: str, path: str) -> str:
        return build_abfs_uri(container, path)

    def read_csv(self, container: str, path: str, **kwargs) -> pd.DataFrame:
        """Read a CSV from ADLS into a pandas DataFrame.

        `storage_options` may be provided in kwargs (it will be forwarded to
        the pandas reader when using a URL form supported by fsspec/adlfs).
        """
        uri = self.path(container, path)
        storage_options = kwargs.pop("storage_options", {})
        return pd.read_csv(uri, storage_options=storage_options, **kwargs)

    def read_parquet(self, container: str, path: str, **kwargs) -> pd.DataFrame:
        """Read a Parquet or Delta-Parquet file/table from ADLS.

        This uses `fsspec` to open the remote file and `pandas.read_parquet`
        to parse it. For Delta tables, see `read_delta_table` below.
        """
        uri = self.path(container, path)
        fs, path_in_fs = fsspec.core.url_to_fs(uri)
        with fs.open(path_in_fs, "rb") as fh:
            return pd.read_parquet(fh, **kwargs)

    def read_delta_table(self, container: str, table_path: str, **kwargs) -> pd.DataFrame:
        """Read a Delta table using the optional `deltalake` package.

        If `deltalake` is not installed a helpful error is raised. If installed,
        this will attempt to read the table and return a pandas DataFrame.
        """
        try:
            from deltalake import DeltaTable
        except Exception:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Delta support requires the 'deltalake' package. Install it with 'pip install deltalake'"
            )

        uri = self.path(container, table_path)
        dt = DeltaTable(uri)
        return dt.to_pandas(**kwargs)

    def list_files(self, container: str, path: str = ""):
        uri = self.path(container, path)
        fs, _ = fsspec.core.url_to_fs(uri)
        prefix = uri.split("//", 1)[1]
        return fs.ls(prefix)

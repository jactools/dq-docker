import io
import types

import pandas as pd
import pytest

from dq_docker.adls import utils
from dq_docker.adls import client as adls_client_mod
from dq_docker.adls.client import ADLSClient


def test_build_abfs_uri():
    assert utils.build_abfs_uri("mycontainer", "data/file.parquet") == "abfs://mycontainer/data/file.parquet"


def test_env_var_names():
    names = utils.env_var_names()
    expected = [
        "AZURE_STORAGE_ACCOUNT_NAME",
        "AZURE_TENANT_ID",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
    ]
    for n in expected:
        assert n in names


def test_read_csv_calls_pandas(monkeypatch):
    # Ensure the client thinks fsspec is available
    monkeypatch.setattr(adls_client_mod, "fsspec", types.SimpleNamespace())

    called = {}

    def fake_read_csv(uri, storage_options=None, **kwargs):
        called["uri"] = uri
        called["storage_options"] = storage_options
        return pd.DataFrame({"a": [1]})

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    client = ADLSClient()
    df = client.read_csv("container", "path/to/file.csv", storage_options={"opt": "val"})

    assert isinstance(df, pd.DataFrame)
    assert called["uri"] == "abfs://container/path/to/file.csv"
    assert called["storage_options"] == {"opt": "val"}


def test_read_parquet_calls_pandas(monkeypatch):
    # Create a fake filesystem that returns a file-like object
    class FakeFS:
        def open(self, path, mode="rb"):
            return io.BytesIO(b"PARQUET")

        def ls(self, prefix):
            return ["file1"]

    fake_fs = FakeFS()

    def fake_url_to_fs(uri):
        # return fake fs and the path portion
        return fake_fs, uri.split("//", 1)[1]

    fake_core = types.SimpleNamespace(url_to_fs=fake_url_to_fs)
    monkeypatch.setattr(adls_client_mod, "fsspec", types.SimpleNamespace(core=fake_core))

    called = {}

    def fake_read_parquet(fh, **kwargs):
        # should receive a file-like handle
        assert hasattr(fh, "read")
        called["read"] = True
        return pd.DataFrame({"p": [2]})

    monkeypatch.setattr(pd, "read_parquet", fake_read_parquet)

    client = ADLSClient()
    df = client.read_parquet("container", "dir/file.parquet")

    assert called.get("read", False) is True
    assert isinstance(df, pd.DataFrame)


def test_read_delta_table_requires_deltalake(monkeypatch):
    # Ensure fsspec present for instantiation
    monkeypatch.setattr(adls_client_mod, "fsspec", types.SimpleNamespace())
    client = ADLSClient()
    # If deltalake is not installed, we should get a RuntimeError
    with pytest.raises(RuntimeError):
        client.read_delta_table("container", "some/table/path")

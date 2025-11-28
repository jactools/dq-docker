import os
import pytest

from dq_docker.adls import ADLSClient


def _has_adls_creds():
    # Consider ADLS credentials present only when we have a usable
    # authentication combination. Accept either:
    #  - `AZURE_STORAGE_CONNECTION_STRING`, OR
    #  - `AZURE_STORAGE_ACCOUNT_NAME` plus one of `AZURE_STORAGE_ACCOUNT_KEY`
    #    or `AZURE_STORAGE_SAS_TOKEN`/`AZURE_STORAGE_SAS`.
    if os.environ.get("AZURE_STORAGE_CONNECTION_STRING"):
        return True
    account = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
    key = os.environ.get("AZURE_STORAGE_ACCOUNT_KEY")
    sas = os.environ.get("AZURE_STORAGE_SAS_TOKEN") or os.environ.get("AZURE_STORAGE_SAS")
    return bool(account and (key or sas))


@pytest.mark.skipif(not _has_adls_creds(), reason="No ADLS credentials in environment")
def test_read_csv_smoke():
    client = ADLSClient()
    # Note: user should set these env vars or adjust container/path for their test
    container = os.environ.get("DQ_TEST_ADLS_CONTAINER") or "samplecontainer"
    path = os.environ.get("DQ_TEST_ADLS_PATH") or "sample_data/customers/customers_2019.csv"
    df = client.read_csv(container, path)
    assert df is not None
    assert not df.empty

import os
import pytest

from dq_docker.adls import ADLSClient


def _has_adls_creds():
    return bool(os.environ.get("AZURE_STORAGE_ACCOUNT_NAME"))


@pytest.mark.skipif(not _has_adls_creds(), reason="No ADLS credentials in environment")
def test_read_csv_smoke():
    client = ADLSClient()
    # Note: user should set these env vars or adjust container/path for their test
    container = os.environ.get("DQ_TEST_ADLS_CONTAINER") or "samplecontainer"
    path = os.environ.get("DQ_TEST_ADLS_PATH") or "sample_data/customers/customers_2019.csv"
    df = client.read_csv(container, path)
    assert df is not None
    assert not df.empty

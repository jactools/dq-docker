import sys
import types
import os

import pytest
import importlib


class _FakeSecret:
    def __init__(self, value):
        self.value = value


class _FakeSecretClient:
    def __init__(self, vault_url, credential=None):
        self.vault_url = vault_url

    def get_secret(self, name):
        # return a predictable value based on name
        return _FakeSecret(f"{name}-value")


class _FakeDefaultCredential:
    pass


def test_from_key_vault_sets_env_vars(monkeypatch, tmp_path):
    # Create fake azure modules
    azure = types.ModuleType("azure")
    azure_identity = types.ModuleType("azure.identity")
    azure_kv = types.ModuleType("azure.keyvault")
    azure_kv_secrets = types.ModuleType("azure.keyvault.secrets")

    azure_identity.DefaultAzureCredential = lambda: _FakeDefaultCredential()
    azure_kv_secrets.SecretClient = _FakeSecretClient

    monkeypatch.setitem(sys.modules, "azure", azure)
    monkeypatch.setitem(sys.modules, "azure.identity", azure_identity)
    monkeypatch.setitem(sys.modules, "azure.keyvault", azure_kv)
    monkeypatch.setitem(sys.modules, "azure.keyvault.secrets", azure_kv_secrets)

    # Ensure fsspec appears available so ADLSClient can be instantiated
    monkeypatch.setitem(sys.modules, "fsspec", types.SimpleNamespace(core=types.SimpleNamespace(url_to_fs=lambda u: (types.SimpleNamespace(open=lambda p, mode='rb': open(__file__, 'rb')), u.split('//', 1)[1]))))

    # Provide a fake pandas module to avoid importing the real compiled pandas
    # which can cause binary compatibility issues in the test environment.
    monkeypatch.setitem(sys.modules, "pandas", types.SimpleNamespace(read_csv=lambda *a, **k: None, read_parquet=lambda *a, **k: None, DataFrame=object))

    # Import the client module after setting up fake modules so its module-level
    # imports (like `fsspec`) pick up our monkeypatched entries.
    mod = importlib.import_module("dq_docker.adls.client")
    adls_client_mod = importlib.reload(mod)
    ADLSClient = adls_client_mod.ADLSClient

    # Call from_key_vault with custom secret names
    client = ADLSClient.from_key_vault(
        vault_url="https://my-vault.vault.azure.net/",
        account_name_secret="my-account",
        client_id_secret="my-client-id",
        client_secret_secret="my-client-secret",
        tenant_id_secret="my-tenant-id",
    )

    # Ensure env vars were set from the fake secrets
    assert os.environ.get("AZURE_CLIENT_ID") == "my-client-id-value"
    assert os.environ.get("AZURE_CLIENT_SECRET") == "my-client-secret-value"
    assert os.environ.get("AZURE_TENANT_ID") == "my-tenant-id-value"
    # account name optional; should be set by our fake
    assert os.environ.get("AZURE_STORAGE_ACCOUNT_NAME") == "my-account-value"

    assert isinstance(client, ADLSClient)


def test_from_key_vault_missing_packages_raises(monkeypatch):
    # Ensure azure modules are not present
    monkeypatch.setitem(sys.modules, "azure", None)
    # Also ensure fsspec exists to not fail earlier
    monkeypatch.setitem(sys.modules, "fsspec", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "pandas", types.SimpleNamespace(read_csv=lambda *a, **k: None, read_parquet=lambda *a, **k: None, DataFrame=object))

    # Import module so that the function resolution occurs with current sys.modules
    mod = importlib.import_module("dq_docker.adls.client")
    adls_client_mod = importlib.reload(mod)
    ADLSClient = adls_client_mod.ADLSClient

    with pytest.raises(RuntimeError):
        ADLSClient.from_key_vault("https://does-not-matter")


def test_from_key_vault_secret_missing_raises(monkeypatch):
    # Simulate SecretClient.get_secret raising for any secret
    azure_identity = types.ModuleType("azure.identity")
    azure_kv_secrets = types.ModuleType("azure.keyvault.secrets")

    azure_identity.DefaultAzureCredential = lambda: _FakeDefaultCredential()

    class BadSecretClient:
        def __init__(self, vault_url, credential=None):
            pass

        def get_secret(self, name):
            raise Exception("secret not available")

    azure_kv_secrets.SecretClient = BadSecretClient

    monkeypatch.setitem(sys.modules, "azure.identity", azure_identity)
    monkeypatch.setitem(sys.modules, "azure.keyvault.secrets", azure_kv_secrets)
    # Ensure fsspec present so instantiation doesn't fail earlier
    monkeypatch.setitem(sys.modules, "fsspec", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "pandas", types.SimpleNamespace(read_csv=lambda *a, **k: None, read_parquet=lambda *a, **k: None, DataFrame=object))

    mod = importlib.import_module("dq_docker.adls.client")
    adls_client_mod = importlib.reload(mod)
    ADLSClient = adls_client_mod.ADLSClient

    with pytest.raises(RuntimeError):
        ADLSClient.from_key_vault("https://my-vault.vault.azure.net/")


def test_from_key_vault_account_name_optional(monkeypatch):
    # SecretClient returns client and tenant secrets but raises for account name
    azure_identity = types.ModuleType("azure.identity")
    azure_kv_secrets = types.ModuleType("azure.keyvault.secrets")

    azure_identity.DefaultAzureCredential = lambda: _FakeDefaultCredential()

    class PartialSecretClient:
        def __init__(self, vault_url, credential=None):
            pass

        def get_secret(self, name):
            if name == "my-account-name":
                raise Exception("account name not present")
            return _FakeSecret(f"{name}-value")

    azure_kv_secrets.SecretClient = PartialSecretClient

    monkeypatch.setitem(sys.modules, "azure.identity", azure_identity)
    monkeypatch.setitem(sys.modules, "azure.keyvault.secrets", azure_kv_secrets)
    # Ensure fsspec present so instantiation doesn't fail earlier
    monkeypatch.setitem(sys.modules, "fsspec", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "pandas", types.SimpleNamespace(read_csv=lambda *a, **k: None, read_parquet=lambda *a, **k: None))

    # Import client module after monkeypatching so fsspec is available
    adls_client_mod = importlib.import_module("dq_docker.adls.client")
    ADLSClient = adls_client_mod.ADLSClient

    # If account name secret is missing, ADLSClient should still be created
    # Ensure no account name is present in env before calling
    os.environ.pop("AZURE_STORAGE_ACCOUNT_NAME", None)

    client = ADLSClient.from_key_vault(
        vault_url="https://my-vault.vault.azure.net/",
        account_name_secret="my-account-name",
        client_id_secret="my-client-id",
        client_secret_secret="my-client-secret",
        tenant_id_secret="my-tenant-id",
    )

    # AZURE_STORAGE_ACCOUNT_NAME should not be set in the environment
    assert os.environ.get("AZURE_STORAGE_ACCOUNT_NAME") is None
    assert isinstance(client, ADLSClient)

# ADLS Gen2 (Azure Data Lake Storage)


Example (service principal + pandas):

```python
import os
from dq_docker.adls import ADLSClient

# set env vars: AZURE_STORAGE_ACCOUNT_NAME, AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
client = ADLSClient()
df = client.read_parquet('mycontainer', 'sample_data/customers/customers_2020.parquet')
```

Example `profiles.yml` snippet for Great Expectations datasource (abfs):

```yaml
datasources:
	my_adls:
		class_name: Datasource
		execution_engine:
			class_name: PandasExecutionEngine
		data_connectors:
			default_runtime_data_connector_name:
				class_name: RuntimeDataConnector
		reader_options:
			storage_options:
				account_name: ${AZURE_STORAGE_ACCOUNT_NAME}
```

## Secure example (Key Vault)

If you store service-principal credentials or the account name in Azure Key Vault you can construct an `ADLSClient` that reads secrets at runtime. This avoids committing secrets to repo files.

```python
from dq_docker.adls import ADLSClient

# Create a client by fetching secrets from Key Vault. The constructor sets
# AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID and (optionally)
# AZURE_STORAGE_ACCOUNT_NAME from the named secrets in Key Vault.
client = ADLSClient.from_key_vault(
    vault_url="https://my-vault.vault.azure.net/",
    account_name_secret="my-adls-account-name-secret",  # optional
    client_id_secret="my-adls-client-id-secret",
    client_secret_secret="my-adls-client-secret",
    tenant_id_secret="my-adls-tenant-id-secret",
)

df = client.read_parquet('mycontainer', 'sample_data/customers/customers_2020.parquet')

Note: the `ADLSClient.from_key_vault()` helper was added in version `0.2.17`.
```

For Azure-hosted workloads prefer managed identity / `DefaultAzureCredential` and store only the account name in Key Vault (or not at all). The `from_key_vault` helper uses `DefaultAzureCredential` by default so it will work with local dev credentials, service principals, or managed identities.

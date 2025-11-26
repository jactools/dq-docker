# ADLS Gen2 support (dq_docker.adls)

This package contains helper utilities and a tiny `ADLSClient` wrapper for accessing ADLS Gen2
using `adlfs` (fsspec).

Installation

Install the optional dependency to enable ADLS support:

```bash
pip install '.[adls]'
```

Using the client

```python
from dq_docker.adls import ADLSClient

client = ADLSClient()
df = client.read_csv('mycontainer', 'sample_data/customers/customers_2020.csv')
df = client.read_parquet('mycontainer', 'sample_data/customers/customers_2020.parquet')

# Reading a Delta table (requires the optional `deltalake` package):
try:
	df_delta = client.read_delta_table('mycontainer', 'sample_data/delta_table')
except RuntimeError:
	print('Install deltalake to read Delta tables: pip install deltalake')
```

Authentication

- Service principal: set `AZURE_STORAGE_ACCOUNT_NAME`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, and `AZURE_CLIENT_SECRET` in the environment; `adlfs` will pick these up via `azure-identity` if configured.
- Managed Identity: if running in Azure (VM/ACI/Function), `adlfs` and `azure-identity` can use the VM/MSI credentials without env vars.

Advanced

For complex workflows use `adlfs` directly (it exposes fsspec filesystem implementations).

**Secure Examples**

This document collects secure, production-ready patterns for storing and retrieving secrets used by adapter and datasource configurations. It contains platform-specific examples for Azure, AWS, and GCP, as well as CI/CD and Kubernetes snippets. Use these patterns to avoid embedding credentials in repository files.

**Azure Key Vault (Python)**: use `azure-identity` and `azure-keyvault-secrets` with `DefaultAzureCredential` so your code works with local dev creds, service principals, or managed identity in Azure hosted environments.

```py
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

vault_url = "https://my-vault-name.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=vault_url, credential=credential)

# Fetch a secret and set as an environment variable for downstream libraries
db_password = client.get_secret("my-db-password").value
import os
os.environ["DB_PASSWORD"] = db_password

# Now libraries that read env vars (e.g. Great Expectations profiles) can use it
```

**Azure + ADLFS / fsspec**: ADLS clients commonly read credentials from env vars or DefaultAzureCredential. For service principal auth, fetch client secret from Key Vault and set env vars before creating the ADLS client.

```py
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os

vault_url = "https://my-vault.vault.azure.net/"
cred = DefaultAzureCredential()
kv = SecretClient(vault_url=vault_url, credential=cred)

os.environ["AZURE_CLIENT_ID"] = kv.get_secret("adls-client-id").value
os.environ["AZURE_CLIENT_SECRET"] = kv.get_secret("adls-client-secret").value
os.environ["AZURE_TENANT_ID"] = kv.get_secret("adls-tenant-id").value

# Then create ADLSClient or fsspec filesystem which reads env vars

Tip: `ADLSClient.from_key_vault()` (introduced in `0.2.17`) automates fetching these secrets from Key Vault and setting the expected environment variables.
```

**GitHub Actions: retrieve Azure secrets & login**

```yaml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }} # JSON for service principal
      - name: Fetch Key Vault secrets
        run: |
          az keyvault secret download --file secret.txt --id https://my-vault.vault.azure.net/secrets/adls-client-secret
        env:
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

**AWS Secrets Manager (Python)**: use `boto3` to fetch secrets at runtime.

```py
import boto3, os, json

client = boto3.client('secretsmanager', region_name='eu-west-1')
resp = client.get_secret_value(SecretId='my/database/credentials')
data = json.loads(resp['SecretString'])
os.environ['DB_USER'] = data['username']
os.environ['DB_PASSWORD'] = data['password']
```

**GitHub Actions: use AWS Secrets / IAM role**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: eu-west-1
      - name: Fetch secret
        run: |
          aws secretsmanager get-secret-value --secret-id my/database/credentials --query SecretString --output text > secret.json
          export DB_CREDS=$(cat secret.json)
```

**GCP Secret Manager (Python)**:

```py
from google.cloud import secretmanager
import os, json

client = secretmanager.SecretManagerServiceClient()
name = "projects/123456/secrets/my-secret/versions/latest"
resp = client.access_secret_version(name=name)
payload = resp.payload.data.decode('UTF-8')
data = json.loads(payload)
os.environ['DB_PASSWORD'] = data['password']
```

**GitHub Actions: GCP service account secret (service account JSON)**

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up GCP credentials
        run: |
          echo "${{ secrets.GCP_SA_KEY }}" > gcp_key.json
          gcloud auth activate-service-account --key-file=gcp_key.json
```

**dbt / Great Expectations `profiles.yml` secure example**

Use environment variables and load them via CI secrets. In `profiles.yml`:

```yaml
my_profile:
  target: dev
  outputs:
    dev:
      type: postgres
      host: '{{ env_var("DB_HOST") }}'
      user: '{{ env_var("DB_USER") }}'
      pass: '{{ env_var("DB_PASSWORD") }}'
      port: 5432
      dbname: '{{ env_var("DB_NAME") }}'
```

In CI (GitHub Actions), set env vars from secrets:

```yaml
- name: Run dbt tests
  env:
    DB_HOST: ${{ secrets.DB_HOST }}
    DB_USER: ${{ secrets.DB_USER }}
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
    DB_NAME: ${{ secrets.DB_NAME }}
  run: dbt test --profiles-dir .
```

**Kubernetes: mount secrets as files or env vars**

Secret as env var in Pod spec:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: app
    image: myimage:latest
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
```

Or mount as a file:

```yaml
volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
containers:
  - name: app
    volumeMounts:
    - name: secret-volume
      mountPath: /var/secrets
      readOnly: true
```

**Security Tips**
- Do NOT commit service account keys or secret values to source control.
- Prefer managed identity or short-lived credentials where possible.
- Fetch secrets at runtime (startup) and inject via environment or files for downstream libs.
- Limit secret-scoped IAM/Key Vault access to the minimum set of resources.

If you'd like, I can add adapter-specific secure snippets (for example, exact `ADLSClient` usage with Key Vault or S3 presigned credentials). Tell me which adapters to prioritize.

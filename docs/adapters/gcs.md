```markdown
# Google Cloud Storage

- Install extra: `.[gcs]` (package: `gcsfs`)
- Common credentials: set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON key, or rely on GCE/GKE default service account.
- URI scheme: `gs://bucket/path` for fsspec-backed datasources.
- Caveats: ensure the service account has `storage.objects.get` and `storage.objects.list` permissions; avoid embedding keys in commits.

Example (service account + pandas):

```python
import pandas as pd

# export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
df = pd.read_parquet('gs://my-bucket/sample_data/customers.parquet')
```

Example `profiles.yml` snippet for a GE pandas_filesystem datasource using GCS:

```yaml
datasources:
  my_gcs:
    class_name: Datasource
    execution_engine:
      class_name: PandasExecutionEngine
    reader_options:
      storage_options:
        token: ${GOOGLE_APPLICATION_CREDENTIALS}
```

```
# Google Cloud Storage

- Install extra: `.[gcs]` (package: `gcsfs`)
- Common credentials: set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON key, or rely on GCE/GKE default service account.
- URI scheme: `gs://bucket/path` for fsspec-backed datasources.
- Caveats: ensure the service account has `storage.objects.get` and `storage.objects.list` permissions; avoid embedding keys in commits.

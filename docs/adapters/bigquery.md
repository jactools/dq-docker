```markdown
# BigQuery

- Install extra: `.[bigquery]` (package: `google-cloud-bigquery`)
- Credentials: use a service account JSON key (`GOOGLE_APPLICATION_CREDENTIALS`) or work within GCP using default credentials.
- Usage note: BigQuery is a query engine rather than an object store — expect different data access patterns (SQL, export to GCS, or use BigQuery storage API).
- Caveats: consider permissions and dataset location; large exports may incur costs.

Example (read via BigQuery client):

```python
from google.cloud import bigquery
client = bigquery.Client()
query = 'SELECT * FROM `my_project.my_dataset.my_table` LIMIT 10'
df = client.query(query).to_dataframe()
```

Export to GCS (parquet) example (CLI):

```bash
bq extract --destination_format=PARQUET my_project:my_dataset.my_table gs://my-bucket/path/table-*.parquet
```

```
# BigQuery

- Install extra: `.[bigquery]` (package: `google-cloud-bigquery`)
- Credentials: use a service account JSON key (`GOOGLE_APPLICATION_CREDENTIALS`) or work within GCP using default credentials.
- Usage note: BigQuery is a query engine rather than an object store — expect different data access patterns (SQL, export to GCS, or use BigQuery storage API).
- Caveats: consider permissions and dataset location; large exports may incur costs.

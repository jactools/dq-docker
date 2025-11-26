```markdown
# Snowflake

- Install extra: `.[snowflake]` (package: `snowflake-connector-python`)
- Credentials: account, user, password, role, warehouse, and optionally `authenticator` for SSO.
- Usage: use SQL connections via SQLAlchemy or the connector; for large file access use Snowflake stages (e.g., stage -> copy into table) or external stages with cloud storage.
- Caveats: wheels can be large and platform-specific; recommend using platform-provided wheels in CI images.

Example SQLAlchemy connection (pandas):

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}')
df = pd.read_sql('SELECT * FROM my_table LIMIT 10', engine)
```

Example using Snowflake stage to unload data to S3 (SQL):

```sql
COPY INTO @my_stage/my_path/ FROM my_table FILE_FORMAT=(TYPE=PARQUET);
```

```
# Snowflake

- Install extra: `.[snowflake]` (package: `snowflake-connector-python`)
- Credentials: account, user, password, role, warehouse, and optionally `authenticator` for SSO.
- Usage: use SQL connections via SQLAlchemy or the connector; for large file access use Snowflake stages (e.g., stage -> copy into table) or external stages with cloud storage.
- Caveats: wheels can be large and platform-specific; recommend using platform-provided wheels in CI images.

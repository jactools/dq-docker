```markdown
# Postgres

- Install extra: `.[postgres]` (packages: `psycopg2-binary`, `sqlalchemy`)
- Connection string: use `postgresql://user:pass@host:port/dbname` or SQLAlchemy URL; prefer environment variables for secrets.
- Usage: read/write via SQLAlchemy engines or pandas `read_sql` using SQLAlchemy connection.
- Caveats: `psycopg2-binary` is convenient but consider `psycopg2` or system packages for production builds if needed.

Example (SQLAlchemy + pandas):

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://user:password@db.example.com:5432/mydb')
df = pd.read_sql('SELECT * FROM customers LIMIT 10', engine)
```

Example `profiles.yml` snippet for dbt-postgres:

```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: {{ env_var('DB_HOST') }}
      user: {{ env_var('DB_USER') }}
      pass: {{ env_var('DB_PASS') }}
      port: 5432
      dbname: mydb
      schema: public
```

```
# Postgres

- Install extra: `.[postgres]` (packages: `psycopg2-binary`, `sqlalchemy`)
- Connection string: use `postgresql://user:pass@host:port/dbname` or SQLAlchemy URL; prefer environment variables for secrets.
- Usage: read/write via SQLAlchemy engines or pandas `read_sql` using SQLAlchemy connection.
- Caveats: `psycopg2-binary` is convenient but consider `psycopg2` or system packages for production builds if needed.

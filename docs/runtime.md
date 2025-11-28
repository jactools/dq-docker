# Runtime behavior: run_id, DQ_RUN_NAME, and GE store actions

This page documents runtime options and environment variables that affect
validation run metadata and Great Expectations store reconciliation during
container startup.

**Run identifiers and Data Docs**

- **What:** The runtime tags each validation result with a run identifier
  (`run_id`) so Data Docs can group and display runs with a human-friendly
  name and timestamp.
- **Source of run name:**
  - If the environment variable `DQ_RUN_NAME` is set, its value will be
    used as the `run_name` portion of the `run_id`.
  - If `DQ_RUN_NAME` is not set, the runtime generates a deterministic
    default run name using the validation definition name and the UTC
    timestamp: `<definition_name>-YYYYMMDDTHHMMSSZ`.
- **run_id shape:** The runtime constructs a `run_id` mapping used where
  Great Expectations APIs accept rich run information. The mapping contains:
  - `run_name`: human readable name (see above)
  - `run_time`: a timezone-aware UTC `datetime` object (the runtime uses
    a `datetime` object rather than a plain string so GE can produce a
    proper RunIdentifier; callers that only accept strings receive a
    fallback `run_name`).

Why this matters: Data Docs render a friendly label for each validation
run based on the RunIdentifier. Using `DQ_RUN_NAME` lets you group related
validation runs under a stable, human-friendly label.

**Environment examples**

- Run locally with a custom run name:

```bash
# set a custom run name for the current execution
export DQ_RUN_NAME="nightly-sample_customers"
python -m dq_docker.run_adls_checkpoint
```

- Run inside Docker (single command):

```bash
docker run --rm \
  -e DQ_CMD=dq_docker.run_adls_checkpoint \
  -e DQ_PROJECT_ROOT=/usr/src/app \
  -e DQ_RUN_NAME="ci-run-2025-11-28" \
  -v "$PWD":/usr/src/app \
  <image>
```

- Set `DQ_RUN_NAME` in a `docker-compose.yml` service:

```yaml
services:
  dq:
    image: myorg/dq_docker:latest
    environment:
      - DQ_CMD=dq_docker.run_adls_checkpoint
      - DQ_PROJECT_ROOT=/usr/src/app
      - DQ_RUN_NAME=nightly-sample_customers
    volumes:
      - ./:/usr/src/app
```

**GE store reconciliation on startup (`GE_STORE_ACTION`)**

At startup the runtime can attempt to reconcile or clear Great
Expectations stores (`ValidationDefinition` and `Checkpoint` stores) to
avoid pydantic deserialization crashes caused by stale serialized objects.
This behavior is controlled by the `GE_STORE_ACTION` environment variable.

Accepted values:

- `none` (default): do nothing.
- `repair`: non-destructive — list store keys and attempt to read each
  stored object; if an entry fails to deserialize it will be deleted.
- `clear`: destructive — attempt to delete all keys in ValidationDefinition
  and Checkpoint stores.
- `repair_and_clear` or `clear_and_repair`: combined behavior (the runtime
  will clear then repair).

Usage notes:

- `repair` is safe for development and debugging when the runtime crashes
  on startup due to stale artifacts. Prefer `none` for production unless an
  administrator explicitly wants store modifications.
- The reconciliation logic is best-effort: it uses store manager APIs
  (`list`/`all` + `get`/`delete` or `add_or_update`) where available and
  ignores failures that cannot be fixed automatically.

**CLI: `scripts/manage_ge_store.py`**

For more control, the repository includes a small management script that
lets you inspect, repair, or clear the GE store interactively from your
local workstation. Example usage:

```bash
# show help
python scripts/manage_ge_store.py --help

# dry-run repair (prints summary)
python scripts/manage_ge_store.py --action repair --dry-run

# destructively clear the GE store (use with caution)
python scripts/manage_ge_store.py --action clear
```

This script is useful when you want to prepare a clean `gx/` state in the
repo before building images or when you want to reproduce problems locally.

**Developer notes**

- The runtime prefers to pass `run_id` dictionaries into `ValidationDefinition.run()` and
  `Checkpoint.run()` so the resulting RunIdentifier contains both a
  `run_name` and `run_time`. For compatibility the code falls back to
  calling `run_name=` or no-arg `run()` if the target object doesn't
  accept the richer signature (tests may provide lightweight doubles that
  only support the simplest calls).
- The default generated run name includes the validation definition name,
  making it easy to identify which definition produced a Data Docs page.

If you'd like this page expanded into a 'how-to' with screenshots of
Data Docs or a step-by-step recovery procedure for corrupted `gx/` stores,
I can add that as a follow-up.

Short examples

- Docker Compose override (development): mount the local project and set a
  friendly `DQ_RUN_NAME` to label runs in Data Docs. Save this as
  `docker-compose.override.yml` next to your `docker-compose.yml`.

```yaml
services:
  dq:
    environment:
      - DQ_CMD=dq_docker.run_adls_checkpoint
      - DQ_PROJECT_ROOT=/usr/src/app
      - DQ_RUN_NAME=dev-sample_customers
    volumes:
      - ./:/usr/src/app
```

- Quick recovery (repair) example: run a non-destructive repair of the GE
  stores from the project root. This uses the included management script
  which performs the same best-effort cleanup available via the
  `GE_STORE_ACTION` runtime flag.

```bash
# Inspect what would be repaired (dry-run)
python scripts/manage_ge_store.py --action repair --dry-run

# Perform repair (non-destructive)
python scripts/manage_ge_store.py --action repair

# Or run the container and let the runtime perform a repair at startup
# (useful for CI or ephemeral containers)
GE_STORE_ACTION=repair DQ_RUN_NAME="ci-$(date -u +%Y%m%dT%H%M%SZ)" ./runit.sh
```
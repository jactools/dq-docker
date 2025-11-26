# Local ADLS Testing with Azurite

This document describes how to run a local Azurite blob storage instance, seed it with sample data, and use the repository's helper scripts to test ADLS-related flows without connecting to a real Azure account.

Important: Azurite emulates the Azure Blob service. It does not fully implement ADLS Gen2 hierarchical-namespace features (abfs://) or all filesystem semantics. Use Azurite for blob-level integration tests (upload, list, download). For full ADLS Gen2 behavior use a real storage account.

Quick steps

1. Start Azurite using the included compose file:

```bash
docker compose -f docker-compose.azurite.yml up -d
```

2. Seed Azurite with a container and a small CSV (optional):

```bash
python scripts/seed_azurite.py --container test-container
```

3. List blobs with the test helper (no credentials required for the default Azurite devstore):

```bash
python scripts/test_adls_local.py --list --container test-container --azurite
```

Files added by this repo

- `docker-compose.azurite.yml` — docker-compose configuration to run Azurite (Blob service on port 10000).
- `scripts/seed_azurite.py` — seed script that uploads a small CSV to a container in Azurite.
- `scripts/test_adls_local.py` — helper now supports `--azurite` mode to list blobs using the Azure Blob SDK.

Notes and tips

- The seed script uses the standard Azurite devstore connection string by default. If you run Azurite on a different host/port, set `AZURITE_CONNECTION_STRING` in your environment or pass a custom connection string.
- Azurite is suitable for CI and local smoke tests that don't require ADLS Gen2-specific features like hierarchical namespace or POSIX-style semantics. Keep tests that require true ADLS behavior gated behind integration flags and real credentials.
- Do not commit secrets into `.env`; use `.env.example` as a template and keep `.env` gitignored.

If you need, I can add a small pytest integration that runs when Azurite is available (skipped in CI by default).

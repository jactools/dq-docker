"""Local ADLS test helper

Usage:
  - Configure environment with either Key Vault or direct env vars:
      * Key Vault mode: set `KEY_VAULT_URL` (e.g. https://my-vault.vault.azure.net/)
        and ensure the vault contains the secrets `adls-client-id`,
        `adls-client-secret`, `adls-tenant-id`, and optionally `adls-account-name`.
      * Direct env mode: set `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`,
        `AZURE_TENANT_ID`, and `AZURE_STORAGE_ACCOUNT_NAME` (or pass account
        explicitly when prompted).

  - Run to only check dependencies and env vars:
      python scripts/test_adls_local.py --check

  - Run to list files in a container/path (will attempt network calls):
      python scripts/test_adls_local.py --container my-container --path some/path

This script is designed to be a *local* convenience helper and shouldn't be
committed with secrets. It prints helpful diagnostics and will only perform
network operations when explicitly asked to list files or read data.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional


def check_deps() -> dict:
    """Check optional dependencies and return a map of feature->bool."""
    results = {}
    try:
        import fsspec  # noqa: F401
        results["fsspec"] = True
    except Exception:
        results["fsspec"] = False

    try:
        import azure.identity  # noqa: F401
        import azure.keyvault.secrets  # noqa: F401
        results["azure_keyvault"] = True
    except Exception:
        results["azure_keyvault"] = False

    try:
        import pandas  # noqa: F401
        results["pandas"] = True
    except Exception:
        results["pandas"] = False

    try:
        import deltalake  # noqa: F401
        results["deltalake"] = True
    except Exception:
        results["deltalake"] = False

    return results


def env_summary() -> dict:
    keys = [
        "KEY_VAULT_URL",
        "AZURE_CLIENT_ID",
        "AZURE_CLIENT_SECRET",
        "AZURE_TENANT_ID",
        "AZURE_STORAGE_ACCOUNT_NAME",
    ]
    return {k: bool(os.environ.get(k)) for k in keys}


def make_client_from_env_or_kv(vault_url: Optional[str] = None):
    """Create an ADLSClient using Key Vault (if vault_url provided) or env vars.

    Returns the client instance or raises RuntimeError with a helpful message.
    """
    try:
        from dq_docker.adls.client import ADLSClient
    except Exception as exc:  # pragma: no cover - depends on local environment
        raise RuntimeError(f"Unable to import ADLSClient: {exc}")

    if vault_url:
        print(f"Using Key Vault at: {vault_url}")
        return ADLSClient.from_key_vault(vault_url)

    # fallback to direct env vars
    if not os.environ.get("AZURE_CLIENT_ID"):
        raise RuntimeError("Missing Azure credentials in environment. Set KEY_VAULT_URL or AZURE_CLIENT_ID etc.")
    return ADLSClient()


def list_files(client, container: str, path: str = "") -> None:
    print(f"Listing files in container='{container}' path='{path}'")
    try:
        files = client.list_files(container, path)
        for f in files:
            print(f)
    except Exception as exc:
        print(f"Failed to list files: {exc}")
        raise


def main(argv=None):
    p = argparse.ArgumentParser(description="Local ADLS test helper")
    p.add_argument("--check", action="store_true", help="Check dependencies and env vars")
    p.add_argument("--vault", "-v", dest="vault_url", help="Key Vault URL (optional)")
    p.add_argument("--container", "-c", help="ADLS container name to operate on")
    p.add_argument("--path", "-p", default="", help="Path inside container")
    p.add_argument("--list", action="store_true", help="List files (will perform network I/O)")
    # Note: Azurite support was removed in this branch revert.

    args = p.parse_args(argv)

    deps = check_deps()
    envs = env_summary()

    if args.check:
        print("Dependency check:")
        for k, v in deps.items():
            print(f" - {k}: {'OK' if v else 'MISSING'}")
        print("Environment variables:")
        for k, v in envs.items():
            print(f" - {k}: {'SET' if v else 'MISSING'}")
        sys.exit(0 if all(deps.values()) else 2)

    # If user asked to list, require container
    if args.list and not args.container:
        p.error("--list requires --container")

    if args.list:
        # Create ADLS client (Key Vault or env) and perform listing
        try:
            client = make_client_from_env_or_kv(args.vault_url)
        except Exception as exc:
            print(f"Failed to create ADLS client: {exc}")
            sys.exit(1)

        list_files(client, args.container, args.path)
        return

    # Default: print short help and environment diagnostics
    print("Run with --check to validate dependencies and environment.")
    print("Example (check): python scripts/test_adls_local.py --check")
    print("Example (list): python scripts/test_adls_local.py --list --container mycontainer --vault https://my-vault.vault.azure.net/")


if __name__ == "__main__":
    main()

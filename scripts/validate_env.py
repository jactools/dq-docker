#!/usr/bin/env python3
"""Validate required environment variables for this project.

Usage:
  python scripts/validate_env.py

Exits with code 0 when all required env vars are set, otherwise prints
missing variables and exits with non-zero status.
"""
from __future__ import annotations

import os
import sys
from typing import Dict, List


REQUIRED_VARS: Dict[str, str] = {
    # name: short description
    "DQ_DATA_SOURCE": "Per-data-source mapping name (required for runtime)",
}


OPTIONAL_VARS: Dict[str, str] = {
    "DQ_PROJECT_ROOT": "Project root override (optional)",
    "DQ_CMD": "Module path to run inside container (optional)",
    "DQ_LOG_LEVEL": "Logging level for dq_docker (optional)",
}


def main() -> int:
    missing: List[str] = []
    for name in REQUIRED_VARS:
        if os.environ.get(name) in (None, ""):
            missing.append(name)

    if missing:
        print("ERROR: missing required environment variables:")
        for m in missing:
            print(f" - {m}: {REQUIRED_VARS.get(m, '')}")
        print("\nSet the variables (for example, create a .env or export them) and retry.")
        return 2

    print("All required environment variables are present.")
    print("Optional variables:")
    for name, desc in OPTIONAL_VARS.items():
        print(f" - {name}: {desc} (current='{os.environ.get(name)}')")

    return 0


if __name__ == "__main__":
    sys.exit(main())

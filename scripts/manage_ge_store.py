#!/usr/bin/env python3
"""Manage Great Expectations store entries for this project.

Usage examples:
  # Repair stores (non-destructive)
  python scripts/manage_ge_store.py --action repair

  # Clear stores (destructive) with confirmation
  python scripts/manage_ge_store.py --action clear --force

  # Clear then repair
  python scripts/manage_ge_store.py --action repair_and_clear --force

This script uses the project's installed Great Expectations environment and
the package helpers implemented in `dq_docker.checkpoint`.
"""
from __future__ import annotations

import argparse
import sys
import importlib


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manage Great Expectations store entries for dq_docker")
    parser.add_argument("--action", "-a", required=True, choices=["none", "repair", "clear", "repair_and_clear", "clear_and_repair"], help="Store action to perform")
    parser.add_argument("--force", "-f", action="store_true", help="Bypass confirmation for destructive operations (clear)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args(argv)

    try:
        gx = importlib.import_module("great_expectations")
    except Exception as exc:
        print("ERROR: Could not import great_expectations; ensure it's installed in your environment.", file=sys.stderr)
        raise

    try:
        ctx = gx.get_context()
    except Exception as exc:
        print("ERROR: Could not load Great Expectations DataContext:", exc, file=sys.stderr)
        raise

    try:
        chk = importlib.import_module("dq_docker.checkpoint")
    except Exception as exc:
        print("ERROR: Could not import dq_docker.checkpoint helper functions:", exc, file=sys.stderr)
        raise

    action = args.action.lower()
    do_clear = "clear" in action
    do_repair = "repair" in action

    if do_clear and not args.force:
        confirm = input("CLEAR is destructive. Type 'yes' to proceed: ")
        if confirm.strip().lower() != "yes":
            print("Aborting clear operation.")
            return 2

    summary = {"validation_definitions_deleted": [], "checkpoints_deleted": [], "errors": []}

    if do_clear:
        print("Running clear_ge_store()...")
        try:
            res = chk.clear_ge_store(ctx, verbose=args.verbose)
            print("clear_ge_store result:", res)
            # Merge summary
            for k in ("validation_definitions_deleted", "checkpoints_deleted", "errors"):
                summary[k].extend(res.get(k, []))
        except Exception as exc:
            print("ERROR during clear_ge_store:", exc, file=sys.stderr)
            summary["errors"].append(str(exc))

    if do_repair:
        print("Running repair_ge_store()...")
        try:
            res = chk.repair_ge_store(ctx, verbose=args.verbose)
            print("repair_ge_store result:", res)
            for k in ("validation_definitions_deleted", "checkpoints_deleted", "errors"):
                summary[k].extend(res.get(k, []))
        except Exception as exc:
            print("ERROR during repair_ge_store:", exc, file=sys.stderr)
            summary["errors"].append(str(exc))

    print("Summary:")
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

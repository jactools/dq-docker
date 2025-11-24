#!/usr/bin/env python3
"""Increment the patch version in pyproject.toml using a TOML parser.

This script reads the `[project].version` field, which must be a
semantic version like MAJOR.MINOR.PATCH, increments PATCH by one, and
writes the file back. If the field is missing, the script will set it
to `0.1.1`.

Usage:
  update_pyproject_version.py [pyproject.toml]
"""
from pathlib import Path
import sys

import logging

# Avoid importing `dq_docker` (and thereby `dq_docker.config`) at module
# import time because CI runs this script before environment variables like
# `DQ_DATA_SOURCE` are set. Use a minimal local logging configuration instead.
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
try:
    import toml
except Exception:
    logging.error("This script requires the 'toml' package. Install via 'pip install toml'.")
    raise


def increment_patch(pyproject_path: Path) -> int:
    data = toml.load(pyproject_path)

    project = data.get("project")
    if project is None:
        project = {}
        data["project"] = project

    version = project.get("version")
    if not version:
        new_version = "0.1.1"
    else:
        parts = str(version).split(".")
        # Ensure we have three numeric parts
        while len(parts) < 3:
            parts.append("0")
        try:
            major = int(parts[0])
            minor = int(parts[1])
            patch = int(parts[2])
        except ValueError:
            logging.warning("Unrecognized version format: %s. Setting to 0.1.1", version)
            major, minor, patch = 0, 1, 0
        patch += 1
        new_version = f"{major}.{minor}.{patch}"

    project["version"] = new_version

    # Write back the pyproject.toml
    toml_string = toml.dumps(data)
    pyproject_path.write_text(toml_string, encoding="utf-8")
    logging.info("Updated pyproject.toml version -> %s", new_version)
    return 0


def set_patch_to(pyproject_path: Path, patch_value: int) -> int:
    """Set the patch version to a specific integer value.

    This is used by the PR workflow which wants to set the patch version
    to the PR number (so versions become MAJOR.MINOR.<PR_NUMBER>).
    """
    data = toml.load(pyproject_path)

    project = data.get("project")
    if project is None:
        project = {}
        data["project"] = project

    version = project.get("version")
    if not version:
        major, minor = 0, 1
    else:
        parts = str(version).split(".")
        while len(parts) < 2:
            parts.append("0")
        try:
            major = int(parts[0])
            minor = int(parts[1])
        except ValueError:
            logging.warning("Unrecognized version format: %s. Using 0.1 as base", version)
            major, minor = 0, 1

    new_version = f"{major}.{minor}.{int(patch_value)}"
    project["version"] = new_version

    toml_string = toml.dumps(data)
    pyproject_path.write_text(toml_string, encoding="utf-8")
    logging.info("Set pyproject.toml version -> %s", new_version)
    return 0


def main(argv):
    # Support two modes:
    #  - PR mode: `update_pyproject_version.py <PR_NUMBER> <pyproject.toml>`
    #    -> sets version patch to PR_NUMBER
    #  - Increment mode: `update_pyproject_version.py [pyproject.toml]`
    #    -> increments patch by 1
    if len(argv) > 2 and argv[1].isdigit():
        pr = int(argv[1])
        path = Path(argv[2])
        if not path.exists():
            logging.error("pyproject file not found: %s", path)
            return 2
        return set_patch_to(path, pr)

    path = Path(argv[1]) if len(argv) > 1 else Path("pyproject.toml")
    if not path.exists():
        logging.error("pyproject file not found: %s", path)
        return 2
    return increment_patch(path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))

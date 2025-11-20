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
from dq_docker.logs import configure_logging

configure_logging()
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


def main(argv):
    path = Path(argv[1]) if len(argv) > 1 else Path("pyproject.toml")
    if not path.exists():
        logging.error("pyproject file not found: %s", path)
        return 2
    return increment_patch(path)


if __name__ == '__main__':
    sys.exit(main(sys.argv))

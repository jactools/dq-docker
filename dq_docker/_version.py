from __future__ import annotations

from pathlib import Path
from typing import Optional


def _read_pyproject_version(pyproject_path: Path) -> Optional[str]:
    if not pyproject_path.exists():
        return None
    try:
        try:
            import tomllib as _toml

            with pyproject_path.open("rb") as f:
                data = _toml.load(f)
        except Exception:
            import toml as _toml  # type: ignore

            data = _toml.loads(pyproject_path.read_text())

        project = data.get("project") if isinstance(data, dict) else None
        if project and isinstance(project, dict):
            version = project.get("version")
            if isinstance(version, str):
                return version
    except Exception:
        return None
    return None


def get_version() -> str:
    # Start at package directory and search upward for pyproject.toml
    pkg_dir = Path(__file__).resolve().parent
    search_dir = pkg_dir
    for _ in range(6):
        candidate = search_dir / "pyproject.toml"
        version = _read_pyproject_version(candidate)
        if version:
            return version
        if search_dir.parent == search_dir:
            break
        search_dir = search_dir.parent

    # Fallback to installed package metadata
    try:
        import importlib.metadata as _ilm

        return _ilm.version("dq-docker")
    except Exception:
        return "0.0.0"


__version__ = get_version()
"""Dynamic package version derived from git commit count.

This provides a simple, auto-incrementing patch version using the
repository commit count: MAJOR.MINOR.<commit_count>

It does not modify source files on disk; the computed version is
determined at runtime (or build time if git metadata is available).
"""
from __future__ import annotations

import os
import subprocess

DEFAULT_BASE = (0, 1)

def _get_commit_count() -> int:
    try:
        repo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        out = subprocess.check_output(["git", "rev-list", "--count", "HEAD"], cwd=repo_dir)
        return int(out.strip())
    except Exception:
        # If git is not available or this is an sdist, fallback to 0
        return 0

def get_version() -> str:
    count = _get_commit_count()
    major, minor = DEFAULT_BASE
    return f"{major}.{minor}.{count}"

__version__ = get_version()

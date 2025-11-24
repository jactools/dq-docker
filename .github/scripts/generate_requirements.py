#!/usr/bin/env python3
"""Generate requirements.txt and requirements-dev.txt from pyproject.toml.

This script attempts to use the stdlib `tomllib` (Python 3.11+). If not
available, it falls back to the `toml` package if present.

It writes a `requirements.txt` from `[project].dependencies` and, when
found, a `requirements-dev.txt` from `[project].optional-dependencies.dev` or
`[project].optional-dependencies."dev"` keys commonly used by tooling.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List


def load_toml(path: Path) -> Dict[str, Any]:
    try:
        import tomllib  # Python 3.11+

        return tomllib.loads(path.read_text(encoding="utf8"))
    except Exception:
        try:
            import toml  # type: ignore

            return toml.loads(path.read_text(encoding="utf8"))
        except Exception:
            raise RuntimeError(
                "No TOML parser available: install with 'pip install toml' or run on Python 3.11+"
            )


def normalize_dep(dep: Any) -> str:
    """Turn a dependency entry into a requirements-style string.

    Most entries will be simple strings (e.g. "pandas" or "requests>=2.0").
    TOML tables or markers are not fully supported here; in such a case we
    return the string representation which should be acceptable for most
    pip installers.
    """
    if isinstance(dep, str):
        return dep
    # Some pyproject writers produce inline tables in the list; stringify them
    return str(dep)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        print(f"pyproject.toml not found at {pyproject}")
        return 2

    data = load_toml(pyproject)
    project = data.get("project", {}) or {}

    deps: List[str] = []
    for d in project.get("dependencies", []) or []:
        deps.append(normalize_dep(d))

    req_file = root / "requirements.txt"
    req_file.write_text("\n".join(deps) + ("\n" if deps else ""), encoding="utf8")
    print(f"Wrote {req_file} ({len(deps)} entries)")

    # Try to write dev requirements from optional-dependencies -> "dev" or 'development'
    opt = project.get("optional-dependencies", {}) or {}
    dev_keys = ["dev", "development", "dev-dependencies"]
    dev_deps: List[str] = []
    for k in dev_keys:
        if k in opt:
            for d in opt.get(k, []) or []:
                dev_deps.append(normalize_dep(d))
            break

    dev_file = root / "requirements-dev.txt"
    if dev_deps:
        dev_file.write_text("\n".join(dev_deps) + "\n", encoding="utf8")
        print(f"Wrote {dev_file} ({len(dev_deps)} entries)")
    else:
        print("No dev dependencies found in pyproject.optional-dependencies; leaving requirements-dev.txt unchanged if present.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

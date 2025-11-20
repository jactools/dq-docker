from __future__ import annotations

from pathlib import Path
from typing import Optional
import re


def _read_pyproject_version(pyproject_path: Path) -> Optional[str]:
    if not pyproject_path.exists():
        return None
    try:
        # Prefer stdlib tomllib (Python 3.11+), fall back to 'toml' package if available
        try:
            import tomllib as _toml

            with pyproject_path.open("rb") as f:
                data = _toml.load(f)
            project = data.get("project") if isinstance(data, dict) else None
            if project and isinstance(project, dict):
                version = project.get("version")
                if isinstance(version, str):
                    return version
        except Exception:
            try:
                import toml as _toml  # type: ignore

                data = _toml.loads(pyproject_path.read_text())
                project = data.get("project") if isinstance(data, dict) else None
                if project and isinstance(project, dict):
                    version = project.get("version")
                    if isinstance(version, str):
                        return version
            except Exception:
                # Last-resort: simple regex search for version = "x.y.z"
                text = pyproject_path.read_text()
                m = re.search(r'^\s*version\s*=\s*"([^"]+)"', text, re.MULTILINE)
                if m:
                    return m.group(1)
    except Exception:
        return None
    return None


def get_version() -> str:
    pkg_dir = Path(__file__).resolve().parent
    search_dir = pkg_dir
    for _ in range(8):
        candidate = search_dir / "pyproject.toml"
        version = _read_pyproject_version(candidate)
        if version:
            return version
        if search_dir.parent == search_dir:
            break
        search_dir = search_dir.parent

    try:
        import importlib.metadata as _ilm

        return _ilm.version("dq-docker")
    except Exception:
        return "0.0.0"


__version__ = get_version()

from __future__ import annotations

import re
from pathlib import Path
from setuptools import setup, find_packages


def _get_version() -> str:
    """Read `pyproject.toml` and extract the project version.

    This uses a simple regex and avoids adding toml as a runtime dependency.
    """
    p = Path(__file__).with_name("pyproject.toml")
    text = p.read_text(encoding="utf8")
    m = re.search(r'^\s*version\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    if m:
        return m.group(1)
    return "0.0.0"


def _get_install_requires() -> list[str]:
    req = Path(__file__).with_name("requirements.txt")
    if req.exists():
        return [l.strip() for l in req.read_text(encoding="utf8").splitlines() if l.strip() and not l.startswith("#")]
    return []


setup(
    name="dq-docker",
    version=_get_version(),
    description="DataQuality Docker project using Great Expectations",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    install_requires=_get_install_requires(),
    python_requires=">=3.8",
)

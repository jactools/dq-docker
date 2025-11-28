"""Top-level data sources loader.

This module provides `DATA_SOURCES` for the package and prefers loading
the YAML file located at `dq_docker/config/data_sources.yml`.
"""
import os
from typing import Dict

# Eager import: require PyYAML at module import time
try:
    import yaml  # type: ignore
except Exception:
    raise RuntimeError("PyYAML is required to load data source files; please add it to your dev requirements")

_here = os.path.dirname(__file__)
# Directory containing per-data-source YAML files
_dir = os.path.join(_here, "config", "data_sources")


def _load_all_yaml(dirpath: str) -> Dict[str, Dict[str, str]]:
    mappings: Dict[str, Dict[str, str]] = {}
    for name in sorted(os.listdir(dirpath)):
        if not (name.endswith(".yml") or name.endswith(".yaml")):
            continue
        key = os.path.splitext(name)[0]
        path = os.path.join(dirpath, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
                if not isinstance(data, dict):
                    raise RuntimeError(f"Data source file {path} must contain a mapping at top-level")
                if key in mappings:
                    raise RuntimeError(f"Duplicate data source key '{key}' from file {path}")
                mappings[key] = {k: v for k, v in data.items()}
        except Exception as exc:
            raise RuntimeError(f"Failed to load data source file {path}: {exc}") from exc
    return mappings


# Require the directory to exist and contain at least one YAML file. Fail
# fast to make misconfiguration obvious.
if not os.path.isdir(_dir):
    raise RuntimeError(f"Missing data source directory: {_dir}; create per-source YAML files like 'ds_sample_data.yml'")

DATA_SOURCES = _load_all_yaml(_dir)
if not DATA_SOURCES:
    raise RuntimeError(f"No data source YAML files found in {_dir}; add at least one .yml mapping")

__all__ = ["DATA_SOURCES"]

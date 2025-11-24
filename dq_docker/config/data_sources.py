"""Data source specific configuration loader.

This module loads `data_sources.yml` when PyYAML is available and falls
back to an embedded mapping otherwise. Keeping YAML as the canonical
mapping makes it easy for non-Python tooling to edit the data-source
definitions.
"""
import os
from typing import Dict

_here = os.path.dirname(__file__)
_yaml_path = os.path.join(_here, "data_sources.yml")


def _load_from_yaml(path: str) -> Dict[str, Dict[str, str]]:
    try:
        import yaml  # type: ignore
    except Exception:
        return {}

    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
            return {k: dict(v or {}) for k, v in data.items()}
    except Exception:
        return {}


# Load YAML when available; otherwise use an embedded fallback.
DATA_SOURCES: Dict[str, Dict[str, str]] = {}
if os.path.exists(_yaml_path):
    DATA_SOURCES = _load_from_yaml(_yaml_path)

if not DATA_SOURCES:
    DATA_SOURCES = {
        "ds_sample_data": {
            "source_folder": os.path.join("dq_great_expectations", "sample_data", "customers"),
            "asset_name": "sample_customers",
            "batch_definition_name": "customers_2019.csv",
            "batch_definition_path": "customers_2019.csv",
            "expectation_suite_name": "adls_data_quality_suite",
            "definition_name": "adls_checkpoint",
        }
    }

__all__ = ["DATA_SOURCES"]

"""Data source specific configuration.

This module defines mappings for data sources. Each data source entry
provides the values that other config consumers derive: source_folder,
asset_name, batch definition names/paths, expectation suite and checkpoint
definition name.

Add additional data sources here and the runtime will pick the one
selected by the `DQ_DATA_SOURCE` environment variable (defaults to
`ds_sample_data`).
"""
import os
from typing import Dict

# Relative paths are relative to the project root. Consumers should join
# them with `PROJECT_ROOT` from `adls_config.py`.
DATA_SOURCES: Dict[str, Dict[str, str]] = {
    "ds_sample_data": {
        "source_folder": os.path.join("dq_great_expectations", "sample_data", "customers"),
        "asset_name": "sample_customers",
        "batch_definition_name": "customers_2019.csv",
        "batch_definition_path": "customers_2019.csv",
        "expectation_suite_name": "adls_data_quality_suite",
        "definition_name": "adls_checkpoint",
    },
    # Example placeholder for another data source:
    # "ds_other": {
    #     "source_folder": os.path.join("dq_great_expectations", "other_data", "folder"),
    #     "asset_name": "other_asset",
    #     "batch_definition_name": "file.parquet",
    #     "batch_definition_path": "file.parquet",
    #     "expectation_suite_name": "other_suite",
    #     "definition_name": "other_checkpoint",
    # },
}

__all__ = ["DATA_SOURCES"]

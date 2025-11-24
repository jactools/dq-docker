# Compute PROJECT_ROOT relative to this config file's location so it's stable
# regardless of the current working directory. This should point to the
# repository root. Use two levels up from `dq_docker/config` so when the
# repository is mounted at `/usr/src/app` in the container `PROJECT_ROOT`
# resolves to `/usr/src/app` (not `/usr/src`).
import os
from typing import Dict

# Allow an environment override so container/CI can explicitly set the project
# root without changing code. Fall back to the computed repo root when not set.
_computed_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROJECT_ROOT = os.environ.get("DQ_PROJECT_ROOT", _computed_root)

# Load per-data-source configuration from a separate module. This allows
# multiple data sources to be defined and selected via environment at
# runtime (or in tests) without editing this file.
try:
    from .data_sources import DATA_SOURCES  # type: ignore
except Exception:  # pragma: no cover - defensive import
    DATA_SOURCES: Dict[str, Dict[str, str]] = {}

# Data Docs
DATA_DOCS_SITE_NAME = "local_site"
DATA_DOCS_CONFIG = {
    "class_name": "SiteBuilder",
    "site_name": DATA_DOCS_SITE_NAME,
    "site_index_builder": {"class_name": "DefaultSiteIndexBuilder"},
    "store_backend": {
        "class_name": "FilesystemStoreBackend",
        "base_directory": os.path.join(PROJECT_ROOT, "dq_great_expectations", "uncommitted", "data_docs", DATA_DOCS_SITE_NAME),
    },
}

# Data source selection. The selected key should exist in `DATA_SOURCES`.
# It can be overridden at runtime via the `DQ_DATA_SOURCE` environment variable.
DATA_SOURCE_NAME = os.environ.get("DQ_DATA_SOURCE", "ds_sample_data")

# Default empty values; will be populated from DATA_SOURCES when available.
SOURCE_FOLDER = None
ASSET_NAME = None
BATCH_DEFINITION_NAME = None
BATCH_DEFINITION_PATH = None
EXPECTATION_SUITE_NAME = None
DEFINITION_NAME = None

# Populate values from `DATA_SOURCES` mapping when possible. If the mapping
# is missing or the specific data source isn't present, fall back to the
# legacy defaults so existing deployments keep working.
_ds = DATA_SOURCES.get(DATA_SOURCE_NAME, {})
if _ds:
    # If source_folder was provided as a relative path, join it to PROJECT_ROOT.
    _sf = _ds.get("source_folder")
    if _sf:
        SOURCE_FOLDER = os.path.join(PROJECT_ROOT, _sf) if not os.path.isabs(_sf) else _sf

    ASSET_NAME = _ds.get("asset_name")
    BATCH_DEFINITION_NAME = _ds.get("batch_definition_name")
    BATCH_DEFINITION_PATH = _ds.get("batch_definition_path")
    EXPECTATION_SUITE_NAME = _ds.get("expectation_suite_name")
    DEFINITION_NAME = _ds.get("definition_name")
else:
    # Legacy defaults
    SOURCE_FOLDER = os.path.join(PROJECT_ROOT, "dq_great_expectations", "sample_data", "customers")
    ASSET_NAME = "sample_customers"
    BATCH_DEFINITION_NAME = "customers_2019.csv"
    BATCH_DEFINITION_PATH = "customers_2019.csv"
    EXPECTATION_SUITE_NAME = "adls_data_quality_suite"
    DEFINITION_NAME = "adls_checkpoint"

# Checkpoint/result config
RESULT_FORMAT = {"result_format": "SUMMARY"}

# Action targets (used by the runtime to build action objects)
DATA_DOCS_SITE_NAMES = [DATA_DOCS_SITE_NAME]

__all__ = [
    "PROJECT_ROOT",
    "DATA_DOCS_SITE_NAME",
    "DATA_DOCS_CONFIG",
    "SOURCE_FOLDER",
    "DATA_SOURCE_NAME",
    "ASSET_NAME",
    "BATCH_DEFINITION_NAME",
    "BATCH_DEFINITION_PATH",
    "EXPECTATION_SUITE_NAME",
    "DEFINITION_NAME",
    "RESULT_FORMAT",
    "DATA_DOCS_SITE_NAMES",
]

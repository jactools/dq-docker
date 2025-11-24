# Compute PROJECT_ROOT relative to this config file's location so it's stable
# regardless of the current working directory. This should point to the
# repository root. Use two levels up from `dq_docker/config` so when the
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

# Load per-data-source configuration from the top-level module which is the
# single source of truth for data source mappings.
from dq_docker.data_sources import DATA_SOURCES  # type: ignore

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
DATA_SOURCE_NAME = os.environ.get("DQ_DATA_SOURCE")

# Default empty values; will be populated from DATA_SOURCES if a source is
# selected. We intentionally avoid raising at import time so tests and tools
# can import the package without requiring the environment variable be set.
SOURCE_FOLDER = None
ASSET_NAME = None
BATCH_DEFINITION_NAME = None
BATCH_DEFINITION_PATH = None
EXPECTATION_SUITE_NAME = None
DEFINITION_NAME = None

# Populate values from `DATA_SOURCES` mapping when possible. Only attempt
# to populate when a `DQ_DATA_SOURCE` has been provided; otherwise leave
# values as None so test harnesses and tools can import the package.
def validate_runtime():
    """Validate runtime configuration for production runs.

    This function enforces that `DQ_DATA_SOURCE` is set and that the
    corresponding entry exists in `DATA_SOURCES`. It also populates
    module-level variables from the selected data source so callers who
    import the module after validation see concrete values.
    """
    global DATA_SOURCE_NAME, SOURCE_FOLDER, ASSET_NAME, BATCH_DEFINITION_NAME, BATCH_DEFINITION_PATH, EXPECTATION_SUITE_NAME, DEFINITION_NAME

    DATA_SOURCE_NAME = os.environ.get("DQ_DATA_SOURCE")
    if not DATA_SOURCE_NAME:
        raise RuntimeError("DQ_DATA_SOURCE environment variable must be set and point to a known data source")

    _ds = DATA_SOURCES.get(DATA_SOURCE_NAME)
    if _ds is None:
        raise RuntimeError(f"Data source '{DATA_SOURCE_NAME}' not found in DATA_SOURCES mapping")

    _sf = _ds.get("source_folder")
    if _sf:
        SOURCE_FOLDER = os.path.join(PROJECT_ROOT, _sf) if not os.path.isabs(_sf) else _sf

    ASSET_NAME = _ds.get("asset_name")
    BATCH_DEFINITION_NAME = _ds.get("batch_definition_name")
    BATCH_DEFINITION_PATH = _ds.get("batch_definition_path")
    EXPECTATION_SUITE_NAME = _ds.get("expectation_suite_name")
    DEFINITION_NAME = _ds.get("definition_name")

if DATA_SOURCE_NAME:
    _ds = DATA_SOURCES.get(DATA_SOURCE_NAME)
    if _ds is None:
        raise RuntimeError(f"Data source '{DATA_SOURCE_NAME}' not found in DATA_SOURCES mapping")

    # Populate values from the data-source mapping.
    _sf = _ds.get("source_folder")
    if _sf:
        SOURCE_FOLDER = os.path.join(PROJECT_ROOT, _sf) if not os.path.isabs(_sf) else _sf

    ASSET_NAME = _ds.get("asset_name")
    BATCH_DEFINITION_NAME = _ds.get("batch_definition_name")
    BATCH_DEFINITION_PATH = _ds.get("batch_definition_path")
    EXPECTATION_SUITE_NAME = _ds.get("expectation_suite_name")
    DEFINITION_NAME = _ds.get("definition_name")
else:
    # Ensure names exist in the module namespace even when not populated.
    ASSET_NAME = None
    BATCH_DEFINITION_NAME = None
    BATCH_DEFINITION_PATH = None
    EXPECTATION_SUITE_NAME = None
    DEFINITION_NAME = None

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

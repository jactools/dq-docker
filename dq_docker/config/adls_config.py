# Compute PROJECT_ROOT relative to this config file's location so it's stable
# regardless of the current working directory. This should point to the
# repository root. Use two levels up from `dq_docker/config` so when the
# repository is mounted at `/usr/src/app` in the container `PROJECT_ROOT`
# resolves to `/usr/src/app` (not `/usr/src`).
import os
# Allow an environment override so container/CI can explicitly set the project
# root without changing code. Fall back to the computed repo root when not set.
_computed_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROJECT_ROOT = os.environ.get("DQ_PROJECT_ROOT", _computed_root)

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

# Data source / asset configuration
SOURCE_FOLDER = os.path.join(PROJECT_ROOT, "dq_great_expectations", "sample_data", "customers")
DATA_SOURCE_NAME = "ds_sample_data"
ASSET_NAME = "sample_customers"

# Batch definition
BATCH_DEFINITION_NAME = "customers_2019.csv"
BATCH_DEFINITION_PATH = "customers_2019.csv"

# Expectation suite and checkpoint names
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

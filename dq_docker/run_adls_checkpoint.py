import os
from pathlib import Path

from .expectations import build_expectation_suite
from .logs import configure_logging, get_logger
from .data_source import ensure_pandas_filesystem, ensure_csv_asset
from .batch_definition import ensure_batch_definition
from .batch_definition import get_batch_and_preview
from .expectation_suite import add_suite_to_context
from .validation_definition import create_or_get_validation_definition
from .checkpoint import create_and_run_checkpoint

from .config import gx_config as cfg

# Eager imports: require Great Expectations at module import time
import great_expectations as gx
from great_expectations.checkpoint import UpdateDataDocsAction

# Expose module-level names for backwards compatibility with tests and
# external callers. These will be refreshed inside `main()` after
# `cfg.validate_runtime()` is called in runtime scenarios.
PROJECT_ROOT = cfg.PROJECT_ROOT
DATA_DOCS_SITE_NAME = cfg.DATA_DOCS_SITE_NAME
DATA_DOCS_CONFIG = cfg.DATA_DOCS_CONFIG
SOURCE_FOLDER = cfg.SOURCE_FOLDER
DATA_SOURCE_NAME = cfg.DATA_SOURCE_NAME
ASSET_NAME = cfg.ASSET_NAME
BATCH_DEFINITION_NAME = cfg.BATCH_DEFINITION_NAME
BATCH_DEFINITION_PATH = cfg.BATCH_DEFINITION_PATH
EXPECTATION_SUITE_NAME = cfg.EXPECTATION_SUITE_NAME
DEFINITION_NAME = cfg.DEFINITION_NAME
RESULT_FORMAT = cfg.RESULT_FORMAT
DATA_DOCS_SITE_NAMES = cfg.DATA_DOCS_SITE_NAMES

configure_logging()
logger = get_logger(__name__)

# local helpers (imported at module level so unit tests can monkeypatch them)
from .context import get_context
from .data_docs import ensure_data_docs_site, get_data_docs_urls
from .validator import run_validations


def main():
    """Orchestrate creating datasources, suites, validation and checkpoint.

    The function uses lazy imports of Great Expectations internals so tests
    can monkeypatch `great_expectations` when needed.
    """
    # Great Expectations is imported at module level; if unavailable the
    # import would have failed earlier and this function will not execute.

    logger.info("Attempting to initialize/load project in: %s", PROJECT_ROOT)

    # initialize context and docs
    context = get_context(PROJECT_ROOT)
    if context is None:
        logger.error("Cannot proceed without a Great Expectations context.")
        return

    ensure_data_docs_site(context, DATA_DOCS_SITE_NAME, DATA_DOCS_CONFIG)
    logger.info("✅ Great Expectations Data Context is ready.")

    from dq_docker.data_sources import DATA_SOURCES as ALL_DATA_SOURCES

    urls = run_validations(
        context,
        ALL_DATA_SOURCES,
        cfg.DATA_SOURCE_NAME,
        PROJECT_ROOT,
        SOURCE_FOLDER,
        DATA_DOCS_SITE_NAMES,
        RESULT_FORMAT,
    )

    if urls is not None:
        logger.info("✅ Data Docs are available at: %s", urls)


if __name__ == "__main__":
    # Enforce runtime configuration when invoked as a script/module
    cfg.validate_runtime()

    # Refresh module-level names from config after validation
    PROJECT_ROOT = cfg.PROJECT_ROOT
    DATA_DOCS_SITE_NAME = cfg.DATA_DOCS_SITE_NAME
    DATA_DOCS_CONFIG = cfg.DATA_DOCS_CONFIG
    SOURCE_FOLDER = cfg.SOURCE_FOLDER
    DATA_SOURCE_NAME = cfg.DATA_SOURCE_NAME
    ASSET_NAME = cfg.ASSET_NAME
    BATCH_DEFINITION_NAME = cfg.BATCH_DEFINITION_NAME
    BATCH_DEFINITION_PATH = cfg.BATCH_DEFINITION_PATH
    EXPECTATION_SUITE_NAME = cfg.EXPECTATION_SUITE_NAME
    DEFINITION_NAME = cfg.DEFINITION_NAME
    RESULT_FORMAT = cfg.RESULT_FORMAT
    DATA_DOCS_SITE_NAMES = cfg.DATA_DOCS_SITE_NAMES

    main()


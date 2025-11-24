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


def main():
    """Orchestrate creating datasources, suites, validation and checkpoint.

    The function uses lazy imports of Great Expectations internals so tests
    can monkeypatch `great_expectations` when needed.
    """
    try:
        import great_expectations as gx
        from great_expectations.checkpoint import UpdateDataDocsAction
    except Exception:
        logger.error("Great Expectations not available; cannot run checkpoint.")
        return

    logger.info("Attempting to initialize/load project in: %s", PROJECT_ROOT)

    # initialize context and docs
    context = get_context(PROJECT_ROOT)
    if context is None:
        logger.error("Cannot proceed without a Great Expectations context.")
        return

    ensure_data_docs_site(context, DATA_DOCS_SITE_NAME, DATA_DOCS_CONFIG)
    logger.info("✅ Great Expectations Data Context is ready.")

    # Determine which data sources to run. If `cfg.DATA_SOURCE_NAME` is set
    # then only run that one; otherwise validate all configured data sources.
    from dq_docker.data_sources import DATA_SOURCES as ALL_DATA_SOURCES

    selected_name = cfg.DATA_SOURCE_NAME
    if selected_name:
        sources = [(selected_name, ALL_DATA_SOURCES[selected_name])]
    else:
        sources = sorted(ALL_DATA_SOURCES.items())

    for src_name, src_conf in sources:
        logger.info("--- Running validations for data source: %s ---", src_name)

        # Resolve source-specific runtime values (respecting PROJECT_ROOT
        # override that may be set during tests by assigning to module vars).
        sf = src_conf.get("source_folder")
        source_folder = os.path.join(PROJECT_ROOT, sf) if sf and not os.path.isabs(sf) else sf
        asset_name = src_conf.get("asset_name")
        batch_definition_name = src_conf.get("batch_definition_name")
        batch_definition_path = src_conf.get("batch_definition_path")
        expectation_suite_name = src_conf.get("expectation_suite_name")
        definition_name = src_conf.get("definition_name")

        # If test harnesses or callers have monkeypatched module-level SOURCE_FOLDER
        # (e.g. `rac.SOURCE_FOLDER = tmp_path`) prefer that when the resolved
        # per-source path does not exist.
        if not source_folder or not os.path.isdir(source_folder):
            if SOURCE_FOLDER and os.path.isdir(SOURCE_FOLDER):
                source_folder = SOURCE_FOLDER

        # datasource + asset
        data_source = ensure_pandas_filesystem(context, src_name, source_folder)
        file_customers = ensure_csv_asset(data_source, asset_name)

        logger.info("Files: %s", os.listdir(source_folder))

        # batch definition + preview
        batch_definition = ensure_batch_definition(file_customers, batch_definition_name, batch_definition_path)
        batch = get_batch_and_preview(batch_definition)

        # build suite from contract (skip if no batch-definition configured)
        suite = None
        if batch_definition_name:
            # Derive a canonical contract filename from the batch stem. Many
            # batch filenames include a year suffix (e.g. `customers_2019.csv`). The
            # canonical contract filenames used in this project drop that suffix
            # (e.g. `customers.contract.json`). Strip a trailing `_YYYY` from the
            # batch stem to look for the canonical contract name.
            batch_stem = Path(batch_definition_name).stem
            import re

            canonical_stem = re.sub(r"_\d{4}$", "", batch_stem)
            contract_file = Path(PROJECT_ROOT) / "contracts" / f"{canonical_stem}.contract.json"
            try:
                suite = build_expectation_suite(expectation_suite_name, contract_path=str(contract_file))
            except ValueError as exc:
                logger.error("ERROR: expectation contract required but missing or invalid: %s", exc)
                logger.error("Expected contract path: %s", contract_file)
                # Continue to next source rather than aborting entire run so other
                # data sources may still be validated.
                continue
        else:
            # No batch definition configured; create an empty suite placeholder
            from types import SimpleNamespace

            suite = SimpleNamespace()

        add_suite_to_context(context, suite, expectation_suite_name)
        if batch is not None:
            try:
                batch.expectation_suite = suite
            except Exception:
                pass

        # run validation
        validation_definition = create_or_get_validation_definition(context, definition_name, batch_definition, suite)
        validation_results = None
        try:
            validation_results = validation_definition.run()
        except Exception:
            logger.error("ValidationDefinition.run() failed to execute")

        if validation_results and validation_results.get("success"):
            logger.info("✅ Validation succeeded for %s!", src_name)
        else:
            logger.error("❌ Validation failed for %s!", src_name)

        # Prepare actions and checkpoint
        action_list = [UpdateDataDocsAction(name="update_data_docs", site_names=DATA_DOCS_SITE_NAMES)]

        results = create_and_run_checkpoint(context, definition_name, validation_definition, action_list, RESULT_FORMAT)
        if not results or "success" not in results:
            logger.error("❌ Checkpoint run did not return success status for %s.", src_name)

    try:
        logger.info(context.list_data_docs_sites())
    except Exception:
        logger.debug("Context does not expose list_data_docs_sites(); skipping listing.")

    urls = get_data_docs_urls(context)
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


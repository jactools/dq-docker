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

from .config.adls_config import (
    PROJECT_ROOT,
    DATA_DOCS_SITE_NAME,
    DATA_DOCS_CONFIG,
    SOURCE_FOLDER,
    DATA_SOURCE_NAME,
    ASSET_NAME,
    BATCH_DEFINITION_NAME,
    BATCH_DEFINITION_PATH,
    EXPECTATION_SUITE_NAME,
    DEFINITION_NAME,
    RESULT_FORMAT,
    DATA_DOCS_SITE_NAMES,
)

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

    # datasource + asset
    data_source = ensure_pandas_filesystem(context, DATA_SOURCE_NAME, SOURCE_FOLDER)
    file_customers = ensure_csv_asset(data_source, ASSET_NAME)

    logger.info("Files: %s", os.listdir(SOURCE_FOLDER))

    # batch definition + preview
    batch_definition = ensure_batch_definition(file_customers, BATCH_DEFINITION_NAME, BATCH_DEFINITION_PATH)
    batch = get_batch_and_preview(batch_definition)

    # build suite from contract
    contract_file = Path(PROJECT_ROOT) / "contracts" / f"{Path(BATCH_DEFINITION_NAME).stem}.contract.json"
    try:
        suite = build_expectation_suite(EXPECTATION_SUITE_NAME, contract_path=str(contract_file))
    except ValueError as exc:
        logger.error("ERROR: expectation contract required but missing or invalid: %s", exc)
        logger.error("Expected contract path: %s", contract_file)
        return

    add_suite_to_context(context, suite, EXPECTATION_SUITE_NAME)
    if batch is not None:
        try:
            batch.expectation_suite = suite
        except Exception:
            pass

    # run validation
    validation_definition = create_or_get_validation_definition(context, DEFINITION_NAME, batch_definition, suite)
    validation_results = None
    try:
        validation_results = validation_definition.run()
    except Exception:
        logger.error("ValidationDefinition.run() failed to execute")

    if validation_results and validation_results.get("success"):
        logger.info("✅ Validation succeeded!")
    else:
        logger.error("❌ Validation failed!")

    # Prepare actions and checkpoint
    action_list = [UpdateDataDocsAction(name="update_data_docs", site_names=DATA_DOCS_SITE_NAMES)]

    results = create_and_run_checkpoint(context, DEFINITION_NAME, validation_definition, action_list, RESULT_FORMAT)
    if not results or "success" not in results:
        logger.error("❌ Checkpoint run did not return success status.")

    try:
        logger.info(context.list_data_docs_sites())
    except Exception:
        logger.debug("Context does not expose list_data_docs_sites(); skipping listing.")

    urls = get_data_docs_urls(context)
    logger.info("✅ Data Docs are available at: %s", urls)


if __name__ == "__main__":
    main()


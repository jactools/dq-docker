import os
import re
from pathlib import Path
import importlib

from .logs import get_logger
from .data_source import ensure_pandas_filesystem, ensure_csv_asset
from .batch_definition import ensure_batch_definition, get_batch_and_preview
from .expectations import build_expectation_suite
from .expectation_suite import add_suite_to_context
from .validation_definition import create_or_get_validation_definition
from .checkpoint import create_and_run_checkpoint

# Eager imports (remove lazy imports)
import great_expectations as gx  # noqa: F401
from great_expectations.checkpoint import UpdateDataDocsAction

logger = get_logger(__name__)


def run_validations(
    context,
    all_data_sources,
    selected_name,
    project_root,
    module_source_folder,
    data_docs_site_names,
    result_format,
):
    """Run validations for one or more configured data sources.

    Parameters mirror the runtime values in `run_adls_checkpoint.main()` so
    this function can be unit-tested in isolation.
    """

    # Select which sources to run
    if selected_name:
        sources = [(selected_name, all_data_sources[selected_name])]
    else:
        sources = sorted(all_data_sources.items())

    # Allow test harnesses to monkeypatch helper functions on the
    # `dq_docker.run_adls_checkpoint` module. Prefer using any attributes
    # that have been set there so unit tests can intercept behavior.

    rac = importlib.import_module("dq_docker.run_adls_checkpoint")

    ensure_pandas_filesystem_fn = getattr(rac, "ensure_pandas_filesystem", ensure_pandas_filesystem)
    ensure_csv_asset_fn = getattr(rac, "ensure_csv_asset", ensure_csv_asset)
    ensure_batch_definition_fn = getattr(rac, "ensure_batch_definition", ensure_batch_definition)
    get_batch_and_preview_fn = getattr(rac, "get_batch_and_preview", get_batch_and_preview)
    build_expectation_suite_fn = getattr(rac, "build_expectation_suite", build_expectation_suite)
    add_suite_to_context_fn = getattr(rac, "add_suite_to_context", add_suite_to_context)
    create_or_get_validation_definition_fn = getattr(rac, "create_or_get_validation_definition", create_or_get_validation_definition)
    create_and_run_checkpoint_fn = getattr(rac, "create_and_run_checkpoint", create_and_run_checkpoint)

    for src_name, src_conf in sources:
        logger.info("--- Running validations for data source: %s ---", src_name)

        sf = src_conf.get("source_folder")
        source_folder = os.path.join(project_root, sf) if sf and not os.path.isabs(sf) else sf
        asset_name = src_conf.get("asset_name")
        batch_definition_name = src_conf.get("batch_definition_name")
        batch_definition_path = src_conf.get("batch_definition_path")
        expectation_suite_name = src_conf.get("expectation_suite_name")
        definition_name = src_conf.get("definition_name")

        if not source_folder or not os.path.isdir(source_folder):
            if module_source_folder and os.path.isdir(module_source_folder):
                source_folder = module_source_folder

        data_source = ensure_pandas_filesystem_fn(context, src_name, source_folder)
        file_customers = ensure_csv_asset_fn(data_source, asset_name)

        logger.info("Files: %s", os.listdir(source_folder) if source_folder else [])

        batch_definition = ensure_batch_definition_fn(file_customers, batch_definition_name, batch_definition_path)
        batch = get_batch_and_preview_fn(batch_definition)

        suite = None
        if batch_definition_name:
            batch_stem = Path(batch_definition_name).stem
            canonical_stem = re.sub(r"_\d{4}$", "", batch_stem)
            contract_file = Path(project_root) / "contracts" / f"{canonical_stem}.contract.json"
            try:
                suite = build_expectation_suite_fn(expectation_suite_name, contract_path=str(contract_file))
            except ValueError as exc:
                logger.error("ERROR: expectation contract required but missing or invalid: %s", exc)
                logger.error("Expected contract path: %s", contract_file)
                continue
        else:
            from types import SimpleNamespace

            suite = SimpleNamespace()

        add_suite_to_context_fn(context, suite, expectation_suite_name)
        if batch is not None:
            try:
                batch.expectation_suite = suite
            except Exception:
                pass

        validation_definition = create_or_get_validation_definition_fn(context, definition_name, batch_definition, suite)
        validation_results = None
        try:
            validation_results = validation_definition.run()
        except Exception:
            logger.error("ValidationDefinition.run() failed to execute")

        if validation_results and validation_results.get("success"):
            logger.info("✅ Validation succeeded for %s!", src_name)
        else:
            logger.error("❌ Validation failed for %s!", src_name)

        action_list = [UpdateDataDocsAction(name="update_data_docs", site_names=data_docs_site_names)]

        results = create_and_run_checkpoint_fn(context, definition_name, validation_definition, action_list, result_format)
        if not results or "success" not in results:
            logger.error("❌ Checkpoint run did not return success status for %s.", src_name)

    try:
        logger.info(context.list_data_docs_sites())
    except Exception:
        logger.debug("Context does not expose list_data_docs_sites(); skipping listing.")

    # Return data docs urls if available. Prefer a test-harness override
    # on the `dq_docker.run_adls_checkpoint` module so unit tests that
    # monkeypatch `get_data_docs_urls` are respected.
    try:
        gd = getattr(rac, "get_data_docs_urls", None)
        if gd:
            return gd(context)
        from .data_docs import get_data_docs_urls

        return get_data_docs_urls(context)
    except Exception:
        return None

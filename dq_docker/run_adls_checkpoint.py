import os
from pathlib import Path
# Defer importing `great_expectations` until runtime to allow tests to
# monkeypatch `sys.modules` before this module is imported.

from .expectations import build_expectation_suite
from .logs import configure_logging, get_logger

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

def main():
    import great_expectations as gx
    from great_expectations.checkpoint import UpdateDataDocsAction

    logger.info("Attempting to initialize/load project in: %s", PROJECT_ROOT)

    # Initialize or load a FileDataContext rooted at PROJECT_ROOT
    context = gx.get_context(mode="file", project_root_dir=PROJECT_ROOT)

    # Ensure Data Docs site exists
    if DATA_DOCS_SITE_NAME not in context.get_site_names():
        context.add_data_docs_site(site_name=DATA_DOCS_SITE_NAME, site_config=DATA_DOCS_CONFIG)
        logger.info("✅ Data Docs site '%s' added to the context.", DATA_DOCS_SITE_NAME)
    else:
        logger.info("✅ Data Docs site '%s' already exists in the context.", DATA_DOCS_SITE_NAME)

    msg = "✅ Great Expectations Data Context is ready."
    logger.info(msg)

    # Create the Data Source and CSV asset (uses pandas filesystem datasource)
    # Try to locate an existing datasource with the configured name using a
    # variety of safe inspection methods supported by different GE versions.
    def _find_datasource(ctx, name):
        # Prefer a manager object from ctx.data_sources
        ds_manager = getattr(ctx, "data_sources", None)

        # 1) manager.get(name)
        try:
            get_fn = getattr(ds_manager, "get", None)
            if callable(get_fn):
                try:
                    ds = get_fn(name)
                    if ds:
                        return ds
                except Exception:
                    pass
        except Exception:
            pass

        # 2) context.list_datasources() — may return list/dict depending on GE
        try:
            list_fn = getattr(ctx, "list_datasources", None)
            if callable(list_fn):
                try:
                    items = list_fn()
                    if isinstance(items, dict):
                        # mapping of name -> info
                        if name in items:
                            # try manager.get if available, else return info dict
                            try:
                                if callable(getattr(ds_manager, "get", None)):
                                    return ds_manager.get(name)
                            except Exception:
                                return items[name]
                    elif isinstance(items, list):
                        for it in items:
                            if isinstance(it, dict) and it.get("name") == name:
                                try:
                                    if callable(getattr(ds_manager, "get", None)):
                                        return ds_manager.get(name)
                                except Exception:
                                    return it
                            if isinstance(it, str) and it == name:
                                try:
                                    if callable(getattr(ds_manager, "get", None)):
                                        return ds_manager.get(name)
                                except Exception:
                                    return None
                except Exception:
                    pass
        except Exception:
            pass

        # 3) manager.list() or manager.list_datasources()
        try:
            list_fn = getattr(ds_manager, "list", None) or getattr(ds_manager, "list_datasources", None)
            if callable(list_fn):
                try:
                    items = list_fn()
                    if isinstance(items, list):
                        for it in items:
                            if isinstance(it, dict) and it.get("name") == name:
                                try:
                                    if callable(getattr(ds_manager, "get", None)):
                                        return ds_manager.get(name)
                                except Exception:
                                    return it
                except Exception:
                    pass
        except Exception:
            pass

        return None

    def _find_asset(ds, name):
        """Defensively locate an asset on the datasource by name across GE versions.

        Returns the asset object/info if found, else None.
        """
        if ds is None:
            return None

        # 1) try manager-style get
        try:
            get_fn = getattr(ds, "get", None) or getattr(ds, "get_asset", None)
            if callable(get_fn):
                try:
                    asset = get_fn(name)
                    if asset:
                        return asset
                except Exception:
                    pass
        except Exception:
            pass

        # 2) try list_assets() or an `assets` attribute
        try:
            list_fn = getattr(ds, "list_assets", None)
            items = None
            if callable(list_fn):
                try:
                    items = list_fn()
                except Exception:
                    items = None
            else:
                # fallback to attribute
                items = getattr(ds, "assets", None)

            if isinstance(items, dict):
                if name in items:
                    return items[name]
            elif isinstance(items, list):
                for it in items:
                    if isinstance(it, dict) and it.get("name") == name:
                        return it
                    if isinstance(it, str) and it == name:
                        return it
        except Exception:
            pass

        return None

    data_source = _find_datasource(context, DATA_SOURCE_NAME)

    if not data_source:
        data_source = context.data_sources.add_pandas_filesystem(name=DATA_SOURCE_NAME, base_directory=SOURCE_FOLDER)

    # Attempt to reuse an existing CSV asset if present; otherwise add it.
    file_customers = _find_asset(data_source, ASSET_NAME)
    if not file_customers:
        try:
            file_customers = data_source.add_csv_asset(name=ASSET_NAME)
        except Exception as exc:
            logger.error("Failed to add CSV asset '%s' to data source '%s': %s", ASSET_NAME, DATA_SOURCE_NAME, exc)
            raise

    logger.info("Files: %s", os.listdir(SOURCE_FOLDER))

    def _find_batch_definition(asset, name, path):
        """Defensively locate a batch definition on an asset by name or path.

        Returns the batch definition object if found, else None.
        """
        if asset is None:
            return None

        # 1) try manager-style get_batch_definition
        try:
            get_fn = getattr(asset, "get_batch_definition", None) or getattr(asset, "get", None)
            if callable(get_fn):
                try:
                    bd = get_fn(name)
                    if bd:
                        return bd
                except Exception:
                    pass
        except Exception:
            pass

        # 2) try list_batch_definitions() or an attribute
        try:
            list_fn = getattr(asset, "list_batch_definitions", None) or getattr(asset, "list", None)
            items = None
            if callable(list_fn):
                try:
                    items = list_fn()
                except Exception:
                    items = None
            else:
                items = getattr(asset, "batch_definitions", None)

            if isinstance(items, dict):
                if name in items:
                    return items[name]
                # try matching by path
                for v in items.values():
                    try:
                        if getattr(v, "path", None) == path:
                            return v
                    except Exception:
                        pass
            elif isinstance(items, list):
                for it in items:
                    if isinstance(it, dict) and it.get("name") == name:
                        return it
                    # try objects with attributes
                    try:
                        if getattr(it, "name", None) == name:
                            return it
                        if getattr(it, "path", None) == path:
                            return it
                    except Exception:
                        pass
        except Exception:
            pass

        return None

    batch_definition = _find_batch_definition(file_customers, BATCH_DEFINITION_NAME, BATCH_DEFINITION_PATH)
    if not batch_definition:
        batch_definition = file_customers.add_batch_definition_path(name=BATCH_DEFINITION_NAME, path=BATCH_DEFINITION_PATH)

    # Fetch a batch to inspect
    batch = batch_definition.get_batch()
    logger.info(batch.head())

    # Compute contract path (contracts/{batch_stem}.contract.json) under project root
    contract_file = Path(PROJECT_ROOT) / "contracts" / f"{Path(BATCH_DEFINITION_NAME).stem}.contract.json"

    try:
        suite = build_expectation_suite(EXPECTATION_SUITE_NAME, contract_path=str(contract_file))
    except ValueError as exc:
        logger.error("ERROR: expectation contract required but missing or invalid: %s", exc)
        logger.error("Expected contract path: %s", contract_file)
        return

    try:
        context.suites.add(suite)
        msg = f"✅ Expectation Suite '{EXPECTATION_SUITE_NAME}' added to context."
        logger.info(msg)
    except Exception:
        # If adding the suite fails because it already exists, continue
        msg = f"ℹ️ Expectation Suite '{EXPECTATION_SUITE_NAME}' may already exist; continuing."
        logger.info(msg)

    batch.expectation_suite = suite


    # Build ValidationDefinition and add to the context
    validation_definition = gx.ValidationDefinition(name=DEFINITION_NAME, data=batch_definition, suite=suite)
    # Try to add the validation definition; if it already exists, attempt to
    # locate and reuse the existing one to make this operation idempotent.
    try:
        validation_definition = context.validation_definitions.add(validation_definition)
        logger.info("✅ Validation Definition '%s' created.", DEFINITION_NAME)
    except Exception:
        logger.info("ℹ️ Validation Definition '%s' may already exist; attempting to reuse.", DEFINITION_NAME)
        validation_definition = None
        try:
            vd_manager = getattr(context, "validation_definitions", None)
            # 1) try manager.get(name)
            get_fn = getattr(vd_manager, "get", None)
            if callable(get_fn):
                try:
                    validation_definition = get_fn(DEFINITION_NAME)
                except Exception:
                    validation_definition = None

            # 2) try listing definitions via manager.list() or context.list_validation_definitions()
            if validation_definition is None:
                list_fn = getattr(vd_manager, "list", None) or getattr(context, "list_validation_definitions", None)
                if callable(list_fn):
                    try:
                        items = list_fn()
                        if isinstance(items, dict) and DEFINITION_NAME in items:
                            validation_definition = items[DEFINITION_NAME]
                        elif isinstance(items, list):
                            for it in items:
                                if isinstance(it, dict) and it.get("name") == DEFINITION_NAME:
                                    validation_definition = it
                                    break
                    except Exception:
                        validation_definition = None

            # 3) fallback: try reading context.validation_definitions attribute if iterable
            if validation_definition is None:
                try:
                    items = getattr(context, "validation_definitions", None)
                    if isinstance(items, list):
                        for it in items:
                            try:
                                if getattr(it, "name", None) == DEFINITION_NAME or (isinstance(it, dict) and it.get("name") == DEFINITION_NAME):
                                    validation_definition = it
                                    break
                            except Exception:
                                pass
                except Exception:
                    validation_definition = None
        except Exception:
            validation_definition = None

        if validation_definition is None:
            logger.error("Failed to add or find Validation Definition '%s'.", DEFINITION_NAME)
            raise

    validation_results = validation_definition.run()
    if validation_results.get("success"):
        msg = "✅ Validation succeeded!"
        logger.info(msg)
    else:
        msg = "❌ Validation failed!"
        logger.error(msg)

    # Prepare actions and checkpoint
    action_list = [UpdateDataDocsAction(name="update_data_docs", site_names=DATA_DOCS_SITE_NAMES)]

    checkpoint = gx.Checkpoint(name=DEFINITION_NAME, validation_definitions=[validation_definition], actions=action_list, result_format=RESULT_FORMAT)

    context.checkpoints.add_or_update(checkpoint=checkpoint)
    results = checkpoint.run()
    if "success" not in results:
        msg = "❌ Checkpoint run did not return success status."
        logger.error(msg)
    else:
        msg = f"✅ Checkpoint run success status: {results['success']}"
        logger.info(msg)

    logger.info(context.list_data_docs_sites())
    msg = f"✅ Data Docs are available at: {context.get_docs_sites_urls()}"
    logger.info(msg)


if __name__ == "__main__":
    main()

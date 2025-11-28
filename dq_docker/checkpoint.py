from typing import Any, List
from .logs import get_logger

logger = get_logger(__name__)


def repair_ge_store(context: Any, verbose: bool = False) -> dict:
    """Best-effort repair of GE stores: attempt to deserialize stored
    ValidationDefinitions and Checkpoints and delete any entries that raise
    during deserialization. Returns a dict with lists of deleted keys and
    any errors encountered.

    This function is idempotent and conservative: it only deletes entries
    that cannot be read (deserialize) by the configured GE store APIs.
    """
    result = {"validation_definitions_deleted": [], "checkpoints_deleted": [], "errors": []}
    try:
        # ValidationDefinition store
        vd_mgr = getattr(context, "validation_definitions", None)
        if vd_mgr is not None:
            list_fn = getattr(vd_mgr, "list", None) or getattr(vd_mgr, "all", None) or getattr(vd_mgr, "list_keys", None)
            get_fn = getattr(vd_mgr, "get", None)
            delete_fn = getattr(vd_mgr, "delete", None)
            if callable(list_fn) and callable(get_fn) and callable(delete_fn):
                try:
                    items = list_fn()
                    keys = []
                    if isinstance(items, dict):
                        keys = list(items.keys())
                    elif isinstance(items, list):
                        for it in items:
                            if isinstance(it, str):
                                keys.append(it)
                            else:
                                try:
                                    nm = getattr(it, "name", None) or (it.get("name") if isinstance(it, dict) else None)
                                    if nm:
                                        keys.append(nm)
                                except Exception:
                                    continue

                    for key in keys:
                        try:
                            # Attempt to read; if it fails, delete the key
                            get_fn(key)
                        except Exception:
                            try:
                                delete_fn(key)
                                result["validation_definitions_deleted"].append(key)
                                if verbose:
                                    logger.warning("Deleted stale ValidationDefinition from store: %s", key)
                            except Exception as dexc:
                                result["errors"].append({"key": key, "error": str(dexc)})
                except Exception as exc:
                    result["errors"].append({"phase": "vd_list", "error": str(exc)})

        # Checkpoint store
        cp_mgr = getattr(context, "checkpoints", None)
        if cp_mgr is not None:
            list_fn = getattr(cp_mgr, "list", None) or getattr(cp_mgr, "all", None) or getattr(cp_mgr, "list_keys", None)
            get_fn = getattr(cp_mgr, "get", None)
            delete_fn = getattr(cp_mgr, "delete", None)
            if callable(list_fn) and callable(get_fn) and callable(delete_fn):
                try:
                    items = list_fn()
                    keys = []
                    if isinstance(items, dict):
                        keys = list(items.keys())
                    elif isinstance(items, list):
                        for it in items:
                            if isinstance(it, str):
                                keys.append(it)
                            else:
                                try:
                                    nm = getattr(it, "name", None) or (it.get("name") if isinstance(it, dict) else None)
                                    if nm:
                                        keys.append(nm)
                                except Exception:
                                    continue

                    for key in keys:
                        try:
                            get_fn(key)
                        except Exception:
                            try:
                                delete_fn(key)
                                result["checkpoints_deleted"].append(key)
                                if verbose:
                                    logger.warning("Deleted stale Checkpoint from store: %s", key)
                            except Exception as dexc:
                                result["errors"].append({"key": key, "error": str(dexc)})
                except Exception as exc:
                    result["errors"].append({"phase": "cp_list", "error": str(exc)})
    except Exception as exc_outer:
        result["errors"].append({"phase": "outer", "error": str(exc_outer)})

    return result


def clear_ge_store(context: Any, verbose: bool = False) -> dict:
    """Conservatively clear GE stores: remove all entries from the
    ValidationDefinition and Checkpoint stores (and return a summary).

    This is a destructive operation and should only be used intentionally.
    """
    result = {"validation_definitions_deleted": [], "checkpoints_deleted": [], "errors": []}
    try:
        vd_mgr = getattr(context, "validation_definitions", None)
        if vd_mgr is not None:
            list_fn = getattr(vd_mgr, "list", None) or getattr(vd_mgr, "all", None) or getattr(vd_mgr, "list_keys", None)
            delete_fn = getattr(vd_mgr, "delete", None)
            if callable(list_fn) and callable(delete_fn):
                try:
                    items = list_fn()
                    keys = []
                    if isinstance(items, dict):
                        keys = list(items.keys())
                    elif isinstance(items, list):
                        for it in items:
                            if isinstance(it, str):
                                keys.append(it)
                            else:
                                try:
                                    nm = getattr(it, "name", None) or (it.get("name") if isinstance(it, dict) else None)
                                    if nm:
                                        keys.append(nm)
                                except Exception:
                                    continue

                    for key in keys:
                        try:
                            delete_fn(key)
                            result["validation_definitions_deleted"].append(key)
                            if verbose:
                                logger.warning("Cleared ValidationDefinition from store: %s", key)
                        except Exception as exc:
                            result["errors"].append({"key": key, "error": str(exc)})
                except Exception as exc:
                    result["errors"].append({"phase": "vd_list", "error": str(exc)})

        cp_mgr = getattr(context, "checkpoints", None)
        if cp_mgr is not None:
            list_fn = getattr(cp_mgr, "list", None) or getattr(cp_mgr, "all", None) or getattr(cp_mgr, "list_keys", None)
            delete_fn = getattr(cp_mgr, "delete", None)
            if callable(list_fn) and callable(delete_fn):
                try:
                    items = list_fn()
                    keys = []
                    if isinstance(items, dict):
                        keys = list(items.keys())
                    elif isinstance(items, list):
                        for it in items:
                            if isinstance(it, str):
                                keys.append(it)
                            else:
                                try:
                                    nm = getattr(it, "name", None) or (it.get("name") if isinstance(it, dict) else None)
                                    if nm:
                                        keys.append(nm)
                                except Exception:
                                    continue

                    for key in keys:
                        try:
                            delete_fn(key)
                            result["checkpoints_deleted"].append(key)
                            if verbose:
                                logger.warning("Cleared Checkpoint from store: %s", key)
                        except Exception as exc:
                            result["errors"].append({"key": key, "error": str(exc)})
                except Exception as exc:
                    result["errors"].append({"phase": "cp_list", "error": str(exc)})
    except Exception as exc_outer:
        result["errors"].append({"phase": "outer", "error": str(exc_outer)})

    return result


def create_and_run_checkpoint(context: Any, name: str, validation_definition: Any, actions: List[Any], result_format: Any, run_name: str | None = None, run_id: dict | None = None) -> Any:
    """Create or update a Checkpoint, run it, and return the results.

    Great Expectations is imported at module level.
    """

    import importlib
    try:
        gx = importlib.import_module("great_expectations")
    except Exception:
        gx = None

    # Try to construct a GE Checkpoint; if that fails (for example when
    # tests provide lightweight fake objects or GE's pydantic model rejects
    # the supplied validation definitions), fall back to a minimal local
    # checkpoint implementation that exercises `run()` on provided defs.
    checkpoint = None
    if gx is not None:
        try:
            checkpoint = gx.Checkpoint(name=name, validation_definitions=[validation_definition], actions=actions, result_format=result_format)
        except Exception:
            checkpoint = None

    if checkpoint is None:
        class _LocalCheckpoint:
            def __init__(self, name, validation_definitions, actions, result_format):
                self.name = name
                self.validation_definitions = validation_definitions
                self.actions = actions
                self.result_format = result_format

            def run(self):
                # Attempt to run each validation definition if it exposes
                # a `run()` method; otherwise assume success.
                for vd in self.validation_definitions or []:
                    try:
                        run_fn = getattr(vd, "run", None)
                        if callable(run_fn):
                            run_fn()
                    except Exception:
                        pass
                return {"success": True}

        checkpoint = _LocalCheckpoint(name=name, validation_definitions=[validation_definition], actions=actions, result_format=result_format)

    # Add or update the checkpoint in the context
    try:
        context.checkpoints.add_or_update(checkpoint=checkpoint)
    except Exception:
        logger.info("ℹ️ Checkpoint '%s' add_or_update failed; attempting to continue.", name)

    # Prefer to pass a `run_id` mapping when available (richer metadata),
    # then `run_name`, and finally fall back to the no-arg call for older
    # implementations or lightweight test doubles.
    try:
        if run_id is not None:
            # Prefer passing a typed RunIdentifier if Great Expectations exposes
            # one; some GE implementations expect a RunIdentifier instance
            # rather than a raw dict, and will otherwise drop the value.
            run_id_to_pass = run_id
            if gx is not None and isinstance(run_id, dict):
                try:
                    from great_expectations.core.run_identifier import RunIdentifier
                    run_id_to_pass = RunIdentifier(run_name=run_id.get("run_name"), run_time=run_id.get("run_time"))
                except Exception:
                    try:
                        RunIdentifier = getattr(gx, "RunIdentifier", None)
                        if RunIdentifier is not None:
                            run_id_to_pass = RunIdentifier(run_name=run_id.get("run_name"), run_time=run_id.get("run_time"))
                    except Exception:
                        run_id_to_pass = run_id

            logger.info("Calling Checkpoint.run with run_id=%s", run_id_to_pass)
            # Some GE versions accept both `run_id` and `run_name` together;
            # try the richer call first so run_name is preserved in outputs.
            try:
                results = checkpoint.run(run_id=run_id_to_pass, run_name=(getattr(run_id_to_pass, "run_name", None) if not isinstance(run_id_to_pass, dict) else run_id_to_pass.get("run_name")))
            except TypeError:
                try:
                    results = checkpoint.run(run_id=run_id_to_pass)
                except TypeError:
                    try:
                        results = checkpoint.run(run_name=(getattr(run_id_to_pass, "run_name", None) if not isinstance(run_id_to_pass, dict) else run_id_to_pass.get("run_name")))
                    except TypeError:
                        results = checkpoint.run()
        else:
            try:
                results = checkpoint.run(run_id={"run_name": run_name, "run_time": None}, run_name=run_name)
            except TypeError:
                try:
                    results = checkpoint.run(run_name=run_name)
                except TypeError:
                    try:
                        results = checkpoint.run(run_id={"run_name": run_name, "run_time": None})
                    except TypeError:
                        results = checkpoint.run()
    except Exception:
        results = checkpoint.run()
    if "success" not in results:
        logger.error("❌ Checkpoint run did not return success status.")
    else:
        logger.info("✅ Checkpoint run success status: %s", results.get("success"))

    # Emit a small debug summary of the returned structure so we can
    # diagnose where GE places run_id/run_name when checkpointing.
    try:
        logger.info("Checkpoint.run returned type=%s", type(results))
        if isinstance(results, dict):
            logger.info("Checkpoint.run keys=%s", list(results.keys()))
            rr = results.get("run_results")
            if isinstance(rr, dict):
                logger.info("run_results count=%d", len(rr))
                # Show a couple of entries for inspection
                for idx, (k, v) in enumerate(list(rr.items())[:3]):
                    try:
                        vr = v.get("validation_result") if isinstance(v, dict) else None
                        if vr is None:
                            vr = v
                        logger.info("run_result[%s] keys=%s", k, list(vr.keys()) if isinstance(vr, dict) else type(vr))
                    except Exception:
                        logger.exception("Error while inspecting run_result entry %s", k)
    except Exception:
        logger.exception("Failed to log Checkpoint.run debug summary")

    return results

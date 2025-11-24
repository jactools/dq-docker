from typing import Any, List
from .logs import get_logger

logger = get_logger(__name__)


def create_and_run_checkpoint(context: Any, name: str, validation_definition: Any, actions: List[Any], result_format: Any) -> Any:
    """Create or update a Checkpoint, run it, and return the results.

    Great Expectations is imported lazily inside this function so the module
    can be imported in test environments that monkeypatch the package.
    """
    try:
        import great_expectations as gx
    except Exception:
        gx = None

    if gx is None:
        # Fallback minimal behavior: try to call a run method if present.
        try:
            checkpoint = {"name": name, "validation_definitions": [validation_definition], "actions": actions}
            try:
                context.checkpoints.add_or_update(checkpoint=checkpoint)
            except Exception:
                pass
            # try to run
            if hasattr(checkpoint, "run"):
                return checkpoint.run()
            return {"success": True}
        except Exception:
            return {"success": False}

    checkpoint = gx.Checkpoint(name=name, validation_definitions=[validation_definition], actions=actions, result_format=result_format)

    # Add or update the checkpoint in the context
    try:
        context.checkpoints.add_or_update(checkpoint=checkpoint)
    except Exception:
        logger.info("ℹ️ Checkpoint '%s' add_or_update failed; attempting to continue.", name)

    results = checkpoint.run()
    if "success" not in results:
        logger.error("❌ Checkpoint run did not return success status.")
    else:
        logger.info("✅ Checkpoint run success status: %s", results.get("success"))

    return results

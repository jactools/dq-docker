from typing import Any, List

from .logs import get_logger
from .checkpoint import create_and_run_checkpoint

logger = get_logger(__name__)


def run_checkpoint(context: Any, name: str, validation_definition: Any, actions: List[Any], result_format: Any) -> Any:
    """Wrapper around checkpoint creation and execution.

    This module provides a single entrypoint `run_checkpoint` so higher-level
    orchestration code can import a stable symbol. Internally it delegates to
    `create_and_run_checkpoint` which contains the GE-specific behavior.
    """
    try:
        return create_and_run_checkpoint(context, name, validation_definition, actions, result_format)
    except Exception:
        logger.exception("run_checkpoint encountered an unexpected error")
        return {"success": False}

from typing import Any, Optional
from .logs import get_logger

logger = get_logger(__name__)

# Eager import: require Great Expectations at module import time
import great_expectations as gx


def get_context(project_root: str) -> Optional[Any]:
    """Initialize or load a FileDataContext rooted at `project_root`.

    This function now imports Great Expectations at module import time.
    """
    try:
        ctx = gx.get_context(mode="file", project_root_dir=project_root)
        return ctx
    except Exception as exc:
        logger.error("Failed to initialize/load GE context at %s: %s", project_root, exc)
        raise

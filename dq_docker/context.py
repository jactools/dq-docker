from typing import Any, Optional
from .logs import get_logger

logger = get_logger(__name__)


def get_context(project_root: str) -> Optional[Any]:
    """Lazily initialize or load a FileDataContext rooted at `project_root`.

    Returns the context object or None if Great Expectations is not available.
    """
    try:
        import great_expectations as gx
    except Exception:
        logger.error("Great Expectations is not available in this environment.")
        return None

    try:
        ctx = gx.get_context(mode="file", project_root_dir=project_root)
        return ctx
    except Exception as exc:
        logger.error("Failed to initialize/load GE context at %s: %s", project_root, exc)
        raise

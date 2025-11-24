from typing import Any
from .logs import get_logger

logger = get_logger(__name__)


def add_suite_to_context(context: Any, suite: Any, name: str) -> None:
    """Try to add an ExpectationSuite to the context; ignore if already exists."""
    try:
        context.suites.add(suite)
        logger.info("✅ Expectation Suite '%s' added to context.", name)
    except Exception:
        logger.info("ℹ️ Expectation Suite '%s' may already exist; continuing.", name)

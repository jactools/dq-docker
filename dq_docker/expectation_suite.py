from typing import Any
from types import SimpleNamespace
import importlib

from .logs import get_logger

logger = get_logger(__name__)


def ensure_real_expectation_suite(context: Any, suite: Any, name: str) -> Any:
    """If `suite` is a plain `dict` or `SimpleNamespace`, attempt to
    construct a real Great Expectations `ExpectationSuite` model.

    If GE isn't available or instantiation fails, return the original
    `suite` value unchanged. This keeps test harnesses that inject
    lightweight suite objects working while allowing real GE stores to
    accept the object when possible.
    """
    if suite is None:
        return suite

    # Heuristic: if the object already looks like a GE ExpectationSuite,
    # don't try to convert it.
    try:
        if getattr(suite, "expectation_suite_name", None) or getattr(suite, "name", None):
            return suite
    except Exception:
        pass

    # Only try to convert simple serializable containers.
    if not (isinstance(suite, dict) or isinstance(suite, SimpleNamespace)):
        return suite

    try:
        gx = importlib.import_module("great_expectations")
    except Exception:
        return suite

    es_cls = getattr(gx, "ExpectationSuite", None)
    if not callable(es_cls):
        # Try common alternate import paths
        try:
            mod = importlib.import_module("great_expectations.core.expectation_suite")
            es_cls = getattr(mod, "ExpectationSuite", None)
        except Exception:
            es_cls = None

    if not callable(es_cls):
        return suite

    # Prepare a data dict for construction
    data = dict(suite) if isinstance(suite, dict) else dict(getattr(suite, "__dict__", {}))
    if "expectation_suite_name" not in data and "name" not in data:
        data["expectation_suite_name"] = name
    if "expectations" not in data:
        data["expectations"] = data.get("expectations", [])

    try:
        return es_cls(**data)
    except Exception:
        try:
            # Some GE versions accept a different ctor signature
            return es_cls(expectation_suite_name=name, expectations=data.get("expectations", []))
        except Exception:
            return suite


def add_suite_to_context(context: Any, suite: Any, name: str) -> Any:
    """Try to add an ExpectationSuite to the context and return the
    managed suite object from the context when possible.

    This ensures callers operate on the same ExpectationSuite instance that
    the DataContext manages (avoids GE errors that require the suite to be
    added to the context before updates).
    """
    try:
        context.suites.add(suite)
        logger.info("✅ Expectation Suite '%s' added to context.", name)
    except Exception:
        logger.info("ℹ️ Expectation Suite '%s' may already exist; attempting to reuse.", name)

    # Try to return the suite object managed by the context (if available).
    try:
        suites_manager = getattr(context, "suites", None)
        get_fn = getattr(suites_manager, "get", None)
        if callable(get_fn):
            try:
                managed = get_fn(name)
                if managed is not None:
                    return managed
            except Exception:
                pass

        # Some GE versions expose list/get APIs differently
        list_fn = getattr(suites_manager, "list", None) or getattr(context, "list_expectation_suites", None)
        if callable(list_fn):
            try:
                items = list_fn()
                if isinstance(items, dict) and name in items:
                    return items[name]
                elif isinstance(items, list):
                    for it in items:
                        try:
                            if getattr(it, "expectation_suite_name", None) == name or getattr(it, "name", None) == name:
                                return it
                        except Exception:
                            continue
            except Exception:
                pass
    except Exception:
        pass

    # Fall back to returning the original suite object so tests that provide
    # local/simple suites continue to work.
    return suite
